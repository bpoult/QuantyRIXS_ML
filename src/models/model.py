import numpy as np
import subprocess

from joblib import dump, load
from pathlib import Path
from src.data import load_dataset
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from src.params import CrystalFieldParams
from src.spectra import build_quanty_dicts, generate_inp_quanty, generate_inp_rixs, run_quanty_sim, extract_from_spec, standardize_spectrum
from src.utils import setup_logger, load_config

logger = setup_logger()

def train_model(dataset_path: str, model_path: str = 'models/gradient_boost.joblib'):
    """
    Loads a simulated XAS dataset, splits it into training and test sets,
    trains a MultiOutputRegressor wrapping GradientBoostingRegressor to predict
    crystal field parameters from spectra, and saves the trained model to disk.

    Parameters:
    -----------
    dataset_path : str
        Path to the dataset .h5 file.
    model_path : str
        Path where the trained model will be saved. Default: 'models/gradient_boost.joblib'

    Returns:
    --------
    model : MultiOutputRegressor
        Trained model that maps spectra to crystal field parameters.
    x_test : np.ndarray, shape (N_test, n_energy_points)
        Spectra held out for evaluation.
    y_test : np.ndarray, shape (N_test, n_params)
        True parameter values for the test spectra.
    """

    logger.info(f'Training Beginning')
    spectra, _, params, _, _ = load_dataset(dataset_path)
    
    x = spectra
    # convert array of CrystalFieldParams to a numpy array of parameter values with shape (N, d: num of params)
    y = np.array([p.to_array() for p in params])
    
    # Set test size to 20% of the dataset, random_state/seed to 42 for reproducibility
    x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42)

    # GradientBoostingRegressor only handles 1 output at a time
    base_model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=4
    )

    # MultiOutputRegressor splits y data into d separate targets, and trains one
    # GradientBoostingRegressor for each target
    model = MultiOutputRegressor(base_model)
    model.fit(x_train, y_train)

    # Ensure model directory exists and save trained model to disk
    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    dump(model, model_path)
    logger.info(f'Training Complete')
    

    return model, x_test, y_test

def evaluate_model(model: MultiOutputRegressor, 
             x_test: np.ndarray, 
             y_test: np.ndarray, 
             reference_grid: np.ndarray, 
             output_path: str, 
             PARAMS_SETUP: dict,
             PARAMS_RIXS: dict,
             lua_file="TM_Ledge_spec_job.lua", 
             lua_file_path=None):
    """
    Evaluate the model's prediction of the parameters by re-simulating with run_quanty_sim
    
    Parameters:
    -----------
    model : MultiOutputRegressor
        Trained model that maps spectra to crystal field parameters.
    x_test : np.ndarray, shape (N_test, n_energy_points)
        Spectra held out for evaluation.
    y_test : np.ndarray, shape (N_test, n_params)
        True parameter values for the test spectra.
    output_path : str or Path
        Path to folder containing .lua, .inp_quanty, and .inp_rixs files
    PARAMS_SETUP : dict
        A dictionary containing setup information for the first row transition metal complex
    PARAMS_RIXS : dict
        A dictionary containing RIXS information for the first row transition metal complex
    lua_file : str
        Name of the lua file to execute (default: "greenMLCT_Co3d6_D4h_RCN_conf_job.lua")
    lua_file_path : str or Path, optional
        Directory containing the lua file to copy into folder_path. The lua_file name will be appended.
        If None, assumes lua_file is already in folder_path
    
    Returns:
    --------
    rmse : float
        Root mean squared error between predicted and true spectra averaged across test set.
    cosine_sim : float
        Average cosine similarity between predicted and true spectra across test set.
    """

    logger.info(f'Evaluation Beginning')

    y_pred = model.predict(x_test)

    param_errors = np.abs(y_pred - y_test)
    logger.info(f"MAE ten_dq_i: {param_errors[:, 0].mean():.4f} eV")
    logger.info(f"MAE ten_dq_f: {param_errors[:, 1].mean():.4f} eV")
    logger.info(f"Max error ten_dq_i: {param_errors[:, 0].max():.4f} eV")
    logger.info(f"Max error ten_dq_f: {param_errors[:, 1].max():.4f} eV")
    
    pred_specs = []
    successful_indices = []

    # Loop will handle generating the inp files, simulating a simulation, extracting the spectrum, and standardizing it 
    # to fit the reference_grid and normalized for intensity. Each standardized spectrum will be appended to pred_specs
    for i, p in enumerate(y_pred):
        # Each simulation gets its own subdirectory to avoid file overwrites
        sim_dir = Path(output_path)/ "simulations_with_pred_params" / f"sim_{i:04d}"
        sim_dir.mkdir(parents=True, exist_ok=True)

        ten_dq_i = p[0]
        ten_dq_f = p[1]

        # logger.info(f'Predicted Parameters for simulation {i}:')
        # logger.info(f'ten_dq_i: {ten_dq_i}')
        # logger.info(f'ten_dq_f: {ten_dq_f}')

        cf_params = CrystalFieldParams(ten_dq_i, ten_dq_f)

        # Merge sampled params with fixed constants into Quanty-ready dicts
        params_i, params_f, params_setup, params_rixs = build_quanty_dicts(
            cf_params, PARAMS_SETUP, PARAMS_RIXS
        )

        # Write Quanty input files into the simulation directory
        generate_inp_quanty(params_i, params_f, params_setup, sim_dir, 'GS_Oh.inp_quanty')
        generate_inp_rixs(params_rixs, sim_dir, 'GS_Oh.inp_rixs')

        # Run Quanty and capture stdout to find output spectrum filenames
        try:
            sim_result = run_quanty_sim(sim_dir, lua_file, lua_file_path, timeout=60)
        except subprocess.TimeoutExpired:
            logger.warning(f"[{i+1}/{i}] Simulation timed out — skipping index {i}")
            continue
        except Exception as e:
            logger.error(f"[{i+1}/{i}] Simulation failed: {e} — skipping index {i}")
            continue

        # Parse stdout to find saved .txt spectrum files
        # Ex) 'Saved File: XASisoL3_GS_Oh_1.txt' → 'XASisoL3_GS_Oh_1.txt'
        lines = sim_result.stdout.split('\n')
        saved_files = list(set([line.split()[-1] for line in lines if line.endswith('.txt')]))

         # Check to see if the saved files exist 
        if not saved_files:
            logger.warning(f"[{i+1}/{i}] No output files found — skipping index {i}")
            continue

        # Extract energy grid and intensity array from the first output file
        spec_file = saved_files[0]
        extracted_result = extract_from_spec(folder_path=sim_dir, spec_file=spec_file)

        # Delete .txt spectrum file to save space
        (sim_dir / spec_file).unlink()

        # Standardize then store all predicted spectrums pred_specs array
        standardized = standardize_spectrum(extracted_result['Energy'], extracted_result['Intensity'], reference_grid)
        pred_specs.append(standardized)
        successful_indices.append(i)

    pred_specs = np.stack(pred_specs)
    # Match x_test spectras to successful predicted spectrums to avoid issue in evaluation calculations
    x_test_valid = x_test[successful_indices]

    # Root Mean Square Error
    rmse = np.sqrt(np.sum((x_test_valid - pred_specs) ** 2) / x_test_valid.size)

    # Calculate cosine similarity
    cos_sum = 0
    for true_spec, pred_spec in zip(x_test_valid, pred_specs):
        cos_sum += np.dot(true_spec, pred_spec) / ((np.linalg.norm(true_spec) * np.linalg.norm(pred_spec)))
    cosine_similarity = cos_sum / len(x_test_valid)

    logger.info(f'Evaluation Complete')
    logger.info(f'RMSE: {rmse:.4f}')
    logger.info(f'Cosine Similarity: {cosine_similarity:.4f}')

    return rmse, cosine_similarity

    