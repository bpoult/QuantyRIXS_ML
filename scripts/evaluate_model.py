import numpy as np
import argparse
from src.models.model import train_model, evaluate_model
from src.utils import setup_logger, load_config
from pathlib import Path

logger = setup_logger()

if __name__ == "__main__":
    REPO_ROOT = Path(__file__).parent.parent

    parser = argparse.ArgumentParser(description="Evaluate gradient boosting model on XAS dataset")
    parser.add_argument('--lua_file', type=str, default='TM_Ledge_spec_job.lua')
    parser.add_argument('--lua_file_path', type=str, default=str(REPO_ROOT))
    parser.add_argument('--complex', type=str, default='co_terpy')
    parser.add_argument('--spectrum_type', type=str, default='L3L2')
    parser.add_argument('--initial_state', type=int, default=1)
    parser.add_argument('--mode', type=str, default='CF', choices=['CF', 'CT'])
    parser.add_argument('--config', type=str, default=None)
    args = parser.parse_args()

    complex_spec_type = f'{args.complex}_{args.spectrum_type}_state{args.initial_state}_{args.mode}'
    config_file = args.config if args.config else f'{complex_spec_type}_params.json'
    config = load_config(config_file)

    # Select correct lua file based on mode
    lua_file = 'TM_Ledge_CT_spec_job.lua' if args.mode == 'CT' else args.lua_file

    PARAMS_SETUP = config['PARAMS_SETUP']
    PARAMS_RIXS = config['PARAMS_RIXS']

    dataset_path = REPO_ROOT / 'data' / f'{complex_spec_type}_data' / 'dataset.h5'
    model_path = REPO_ROOT / 'models' / f'gradient_boost_{complex_spec_type}.joblib'

    num_elements = int(round((PARAMS_RIXS['energy_end'] - PARAMS_RIXS['energy_start']) / PARAMS_RIXS['energy_step'])) + 1
    reference_grid = np.linspace(PARAMS_RIXS['energy_start'], PARAMS_RIXS['energy_end'], num=num_elements)

    model, x_test, y_test = train_model(dataset_path, model_path)
    rmse, cosine_sim, pred_specs, pred_params = evaluate_model(model, 
                                                               x_test, 
                                                               y_test, 
                                                               reference_grid=reference_grid,
                                                               output_path=dataset_path.parent, 
                                                               PARAMS_SETUP=PARAMS_SETUP,
                                                               PARAMS_RIXS=PARAMS_RIXS, 
                                                               lua_file=lua_file,
                                                               lua_file_path=args.lua_file_path
    )

    print(f"RMSE: {rmse:.4f}")
    print(f"Cosine similarity: {cosine_sim:.4f}")
    
    # Log predicted parameters
    param_names_cf = ['ten_dq_i', 'ten_dq_f', 'Ds_3d_i', 'Dt_3d_i', 'scalef2', 'scalef4', 'scaleg']
    param_names_ct = ['Delta_L1_i', 'Veg_L1_i', 'Vt2g_L1_i', 'Delta_L2_i', 'Vt2g_L2_i']
    
    param_names = param_names_cf + (param_names_ct if args.mode == 'CT' else [])
    
    logger.info("Mean predicted parameters across test set:")
    mean_pred = np.mean(pred_params, axis=0)
    for name, val in zip(param_names, mean_pred):
        logger.info(f"  {name}: {val:.4f}")