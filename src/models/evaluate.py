import numpy as np
import subprocess

from sklearn.multioutput import MultiOutputRegressor
from src.params import CrystalFieldParams
from src.spectra import build_quanty_dicts, generate_inp_quanty, generate_inp_rixs, run_quanty_sim, extract_from_spec, standardize_spectrum
from src.utils import setup_logger
from pathlib import Path

logger = setup_logger()

def evaluate(model: MultiOutputRegressor, 
             x_test: np.ndarray, 
             y_test: np.ndarray, 
             reference_grid: np.ndarray, 
             output_path: str, 
             PARAMS_SETUP: dict,
             PARAMS_RIXS: dict,
             lua_file="greenMLCT_Co3d6_D4h_RCN_conf_job.lua", 
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

    y_pred = model.predict(x_test)
    pred_specs = []
    successful_indices = []

    for i, p in enumerate(y_pred):
        # Each simulation gets its own subdirectory to avoid file overwrites
        sim_dir = Path(output_path)/ "simulations_with_pred_params" / f"sim_{i:04d}"
        sim_dir.mkdir(parents=True, exist_ok=True)

        ten_dq_i = p[0]
        ten_dq_f = p[1]
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
            sim_result = run_quanty_sim(sim_dir, 'TM_Ledge_spec_job.lua', lua_file_path, timeout=60)
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

        # Store all data into variables to save
        standardized = standardize_spectrum(extracted_result['Energy'], extracted_result['Intensity'], reference_grid)
        pred_specs.append(standardized)
        successful_indices.append(i)

    pred_specs = np.stack(pred_specs)
    x_test_valid = x_test[successful_indices]
    
    rmse = np.sqrt(np.sum((x_test_valid - pred_specs) ** 2) / x_test_valid.size)

    cos_sum = 0
    for true_spec, pred_spec in zip(x_test_valid, pred_specs):
        cos_sum += np.dot(true_spec, pred_spec) / ((np.linalg.norm(true_spec) * np.linalg.norm(pred_spec)))
    cosine_similarity = cos_sum / len(x_test_valid)

    return rmse, cosine_similarity

    