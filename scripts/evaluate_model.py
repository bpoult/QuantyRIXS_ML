import numpy as np
import argparse
from src.models.model import train_model, evaluate_model
from src.utils import setup_logger, load_config
from pathlib import Path

logger = setup_logger()

if __name__ == "__main__":
    REPO_ROOT = Path(__file__).parent.parent

    parser = argparse.ArgumentParser(description="Evaluate gradient boosting model on XAS dataset")
    parser.add_argument('--lua_file', type=str, default=str('TM_Ledge_spec_job.lua'))
    parser.add_argument('--lua_file_path', type=str, default=str(REPO_ROOT))
    parser.add_argument('--complex', type=str, default='co_terpy')
    parser.add_argument('--spectrum_type', type=str, default='L3')
    parser.add_argument('--config', type=str, default='co_terpy_L3_params.json')
    args = parser.parse_args()

    complex_spec_type = f'{args.complex}_{args.spectrum_type}'

    config_file = f"{complex_spec_type}_params.json"
    config = load_config(config_file)
    dataset_path = REPO_ROOT / 'data' / f'{complex_spec_type}_data'
    model_path = REPO_ROOT / 'models' / f'gradient_boost_{complex_spec_type}.joblib'

    PARAMS_SETUP = config['PARAMS_SETUP']
    PARAMS_RIXS = config['PARAMS_RIXS']

    num_elements = int(round((PARAMS_RIXS['energy_end'] - PARAMS_RIXS['energy_start']) / PARAMS_RIXS['energy_step'])) + 1
    reference_grid = np.linspace(PARAMS_RIXS['energy_start'], PARAMS_RIXS['energy_end'], num=num_elements)

    model, x_test, y_test = train_model(dataset_path / 'dataset.h5', model_path)
    rmse, cosine_sim, pred_specs, pred_params = evaluate_model(model, x_test, y_test, reference_grid=reference_grid, output_path=dataset_path, PARAMS_SETUP=PARAMS_SETUP, PARAMS_RIXS=PARAMS_RIXS, lua_file=args.lua_file, lua_file_path=args.lua_file_path)


