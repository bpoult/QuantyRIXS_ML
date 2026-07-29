import numpy as np
import h5py
import argparse
from joblib import load
from pathlib import Path
from scipy.ndimage import gaussian_filter1d
from src.spectra import extract_from_experiment, standardize_spectrum, align_spectrum
from src.utils import setup_logger, load_config
from src.models import evaluate_model

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
    args = parser.parse_args()

    # Set up file paths using flags
    complex_spec_type = f'{args.complex}_{args.spectrum_type}'
    config_file = f"{complex_spec_type}_params.json"
    model_path = f"models/gradient_boost_{complex_spec_type}.joblib"
    reference_path = f"data/{complex_spec_type}_data/{complex_spec_type}_reference_spectrum.npy"

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
    experiment_spectrum = standardize_spectrum(experiment_data['Energy'], experiment_data['Intensity'], reference_grid).reshape(1, -1)

    # Align the desired spectrum to another and log the energy shift
    aligned_experimental, energy_shift = align_spectrum(experiment_spectrum, reference_spectrum, reference_grid)
    logger.info(f"Energy shift applied: {energy_shift:.4f} eV")

    rmse, cosine_sim, pred_specs, pred_params = evaluate_model(model, aligned_experimental, None, reference_grid, args.output_path, PARAMS_SETUP, PARAMS_RIXS, args.lua_file, args.lua_file_path)

    logger.info(
                f"ten_dq_i={pred_params[0]:.3f} | "
                f"ten_dq_f={pred_params[1]:.3f} | "
                f"Ds_3d_i={pred_params[2]:.3f} | "
                f"Dt_3d_i={pred_params[3]:.3f} | "
                f"scalef2={pred_params[4]:.3f} | "
                f"scalef4={pred_params[5]:.3f} | "
                f"scaleg={pred_params[6]:.3f} eV"
            )