import numpy as np
import argparse
from joblib import load
from pathlib import Path
from src.spectra import extract_from_experiment, standardize_spectrum, align_spectrum
from src.utils import setup_logger, load_config
from src.models import evaluate_model
from src.data import load_dataset

logger = setup_logger()
REPO_ROOT = Path(__file__).parent.parent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fit experimental XAS spectrum using trained ML model")
    parser.add_argument('--experiment_file', type=str, required=True, help="Filename of experimental spectrum in data/experimental/")
    parser.add_argument('--output_path', type=str, default=str(REPO_ROOT / 'data' / 'fit_output'))
    parser.add_argument('--lua_file', type=str, default='TM_Ledge_spec_job.lua')
    parser.add_argument('--lua_file_path', type=str, default=str(REPO_ROOT))
    parser.add_argument('--complex', type=str, default='co_terpy')
    parser.add_argument('--spectrum_type', type=str, default='L3')
    parser.add_argument('--initial_state', type=str, default='1')
    parser.add_argument('--mode', type=str, default='CF', choices=['CF', 'CT'])
    args = parser.parse_args()

    # Set up parameters names based on mode
    param_names_cf = ['ten_dq_i', 'ten_dq_f', 'Ds_3d_i', 'Dt_3d_i', 'scalef2', 'scalef4', 'scaleg']
    param_names_ct = ['Delta_L1_i', 'Veg_L1_i', 'Vt2g_L1_i', 'Delta_L2_i', 'Vt2g_L2_i']
    param_names = param_names_cf + (param_names_ct if args.mode == 'CT' else [])

    # Set up file paths using flags
    complex_spec_type = f"{args.complex}_{args.spectrum_type}_state{args.initial_state}_{args.mode}"
    config_file = f"{complex_spec_type}_params.json"
    model_path = f"models/gradient_boost_{complex_spec_type}.joblib"
    reference_path = f"data/{complex_spec_type}_data/{complex_spec_type}_reference_spectrum.npy"
    dataset_path = REPO_ROOT / 'data' / f'{complex_spec_type}_data' / 'dataset.h5'

    # Load in all files
    config = load_config(config_file)
    model = load(model_path)
    reference_spectrum = np.load(reference_path)

    PARAMS_SETUP = config['PARAMS_SETUP']
    PARAMS_RIXS = config['PARAMS_RIXS']
    num_elements = int(round((PARAMS_RIXS['energy_end'] - PARAMS_RIXS['energy_start']) / PARAMS_RIXS['energy_step'])) + 1
    reference_grid = np.linspace(PARAMS_RIXS['energy_start'], PARAMS_RIXS['energy_end'], num=num_elements)

    # Load and standardize the experimental spectrum
    experiment_path = REPO_ROOT / 'data' / 'experimental' / args.experiment_file
    experiment_data = extract_from_experiment(experiment_path)
    experimental_spectrum = standardize_spectrum(experiment_data['Energy'], experiment_data['Intensity'], reference_grid).reshape(1, -1)

    '''
    # Align the desired spectrum to another and log the energy shift
    aligned_experimental, energy_shift = align_spectrum(experiment_spectrum, reference_spectrum, reference_grid)
    logger.info(f"Energy shift applied: {energy_shift:.4f} eV")

    rmse, cosine_sim, pred_specs, pred_params = evaluate_model(model, aligned_experimental, None, reference_grid, args.output_path, PARAMS_SETUP, PARAMS_RIXS, args.lua_file, args.lua_file_path)


    for now, non-aligned experimental spectra is showing better parameter predictions
    '''

    rmse, cosine_sim, pred_specs, pred_params = evaluate_model(model, experimental_spectrum, None, reference_grid, args.output_path, PARAMS_SETUP, PARAMS_RIXS, args.lua_file, args.lua_file_path)
    logger.info("Initial Predictions:")
    logger.info("=" * 40)
    for i, name in enumerate(param_names):
        logger.info(f"  {name:<15} = {pred_params[i]:.4f}")
    logger.info("")

   # Step 1: Access spectra and parameters from dataset
    spectra, _, params, _, _ = load_dataset(dataset_path)
    params = np.array([p.to_array() for p in params[:]])

    # Assign number of candidates in search to be 5% of the data entries
    num_candidates = int(spectra.shape[0] * 0.05)

    # Creates an array of cosine similarities comparing the entire dataset to experimental spectrum
    exp = experimental_spectrum.flatten()
    cos_sims = np.array([
        np.dot(exp, s) / (np.linalg.norm(exp) * np.linalg.norm(s)) 
        for s in spectra
    ])

    # Step 2: Find training spectra with similar parameters to ML prediction
    param_distances = np.linalg.norm(params - pred_params, axis=1)
    candidate_indices = np.argsort(param_distances)[:num_candidates]

    # Step 3: Among those candidates, find best spectral match by cosine similarity
    candidate_cos_sims = cos_sims[candidate_indices]
    # Sort in Greatest to Least order
    best_candidates = candidate_indices[np.argsort(candidate_cos_sims)[::-1]]

    logger.info("Approximate Nearest Neighbors (top 5 by cosine similarity):")
    logger.info("=" * 60)
    # Log the 5 Nearest Neighbors
    for rank, idx in enumerate(best_candidates[:5], start=1):
        logger.info(f"\nRank {rank} — cos_sim={cos_sims[idx]:.4f}")
        for i, name in enumerate(param_names):
            logger.info(f"  {name:<15} = {params[idx, i]:.4f}")

