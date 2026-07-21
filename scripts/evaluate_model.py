import numpy as np
import argparse
from src.models.model import train_model, evaluate_model
from src.utils import setup_logger, load_config
from pathlib import Path

logger = setup_logger()

if __name__ == "__main__":
    REPO_ROOT = Path(__file__).parent.parent

    parser = argparse.ArgumentParser(description="Evaluate gradient boosting model on XAS dataset")
    # parser.add_argument('--dataset_path', type=str, default=str(REPO_ROOT / 'data' / 'medium_dataset' / 'dataset.h5'))
    parser.add_argument('--model_path', type=str, default=str(REPO_ROOT / 'models' / 'gradient_boost.joblib'))
    parser.add_argument('--output_path', type=str, default=str(REPO_ROOT / 'data' / 'eval_output'))
    parser.add_argument('--lua_file', type=str, default=str('TM_Ledge_spec_job.lua'))
    parser.add_argument('--lua_file_path', type=str, default=str(REPO_ROOT))
    parser.add_argument('--config', type=str, default='co_terpy_L3_params.json')
    args = parser.parse_args()

    config = load_config(args.config)
    PARAMS_SETUP = config['PARAMS_SETUP']
    PARAMS_RIXS = config['PARAMS_RIXS']

    if args.config == 'co_terpy_L3_params.json':
        dataset_path = REPO_ROOT / 'data' / 'L3_dataset' / 'dataset.h5'
    else:
        dataset_path = REPO_ROOT / 'data' / 'L3L2_dataset' / 'dataset.h5'

    num_elements = int(round((PARAMS_RIXS['energy_end'] - PARAMS_RIXS['energy_start']) / PARAMS_RIXS['energy_step'])) + 1
    reference_grid = np.linspace(PARAMS_RIXS['energy_start'], PARAMS_RIXS['energy_end'], num=num_elements)

    model, x_test, y_test = train_model(dataset_path, args.model_path)
    rmse, cosine_sim, pred_specs = evaluate_model(model, x_test, y_test, reference_grid, args.output_path, PARAMS_SETUP, PARAMS_RIXS, args.lua_file, args.lua_file_path)

    print(f"RMSE: {rmse:.4f}")
    print(f"Cosine similarity: {cosine_sim:.4f}")

