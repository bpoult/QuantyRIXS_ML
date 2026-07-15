import numpy as np
import h5py
import argparse
from joblib import load
from pathlib import Path
from src.spectra import extract_from_experiment, standardize_spectrum, align_spectrum
from src.utils import setup_logger, load_config
from src.models import evaluate_model

logger = setup_logger()
REPO_ROOT = Path(__file__).parent.parent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fit experimental XAS spectrum using trained ML model")
    parser.add_argument('--experiment_file', type=str, required=True, help="Filename of experimental spectrum in data/experimental/")
    parser.add_argument('--output_path', type=str, default=str(REPO_ROOT / 'data' / 'fit_output'))
    parser.add_argument('--model_path', type=str, default=str(REPO_ROOT / 'models' / 'gradient_boost.joblib'))
    parser.add_argument('--reference_spectrum_path', type=str, default=str(REPO_ROOT / 'data' / 'reference_spectrum.npy'))
    parser.add_argument('--lua_file', type=str, default='TM_Ledge_spec_job.lua')
    parser.add_argument('--lua_file_path', type=str, default=str(REPO_ROOT))
    parser.add_argument('--config', type=str, default='co_terpy_params.json')
    args = parser.parse_args()

    config = load_config(args.config)
    PARAMS_SETUP = config['PARAMS_SETUP']
    PARAMS_RIXS = config['PARAMS_RIXS']
    num_elements = int(round((PARAMS_RIXS['energy_end'] - PARAMS_RIXS['energy_start']) / PARAMS_RIXS['energy_step'])) + 1
    reference_grid = np.linspace(PARAMS_RIXS['energy_start'], PARAMS_RIXS['energy_end'], num=num_elements)

    # Load reference spectrum
    reference_spectrum = np.load(args.reference_spectrum_path)

    # Load and standardize the experimental spectrum
    experiment_path = REPO_ROOT / 'data' / 'experimental' / args.experiment_file
    experiment_data = extract_from_experiment(experiment_path)
    experiment_spectrum = standardize_spectrum(experiment_data['Energy'], experiment_data['Intensity'], reference_grid).reshape(1, -1)

    # Align the desired spectrum to another and log the energy shift
    aligned_experimental, energy_shift = align_spectrum(experiment_spectrum, reference_spectrum, reference_grid)
    logger.info(f"Energy shift applied: {energy_shift:.4f} eV")

    # Run the model evaluation with the aligned spectrum
    model = load(args.model_path)
    rmse, cosine_sim, pred_specs = evaluate_model(model, aligned_experimental, None, reference_grid, args.output_path, PARAMS_SETUP, PARAMS_RIXS, args.lua_file, args.lua_file_path)

    print(f"RMSE: {rmse:.4f}")
    print(f"Cosine similarity: {cosine_sim:.4f}")