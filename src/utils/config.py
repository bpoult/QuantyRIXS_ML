from pathlib import Path
import json

REPO_ROOT = Path(__file__).parent.parent.parent  # QuantyRIXS_ML/src/utils → QuantyRIXS_ML → repo root

def load_config(config_file: str ):
    config_path = REPO_ROOT / 'configs' / config_file

    with open(Path(config_path), 'r') as f:
        config = json.load(f)

    # Set the 'RCN_file" value to QuantyRIXS_ML / config_file because QuantyRIXS_ML is 2 levels above the scripts
    config['PARAMS_SETUP']['rcn_file'] = str(REPO_ROOT / config['PARAMS_SETUP']['rcn_file'])
    
    return config

def load_bounds(bounds_file: str, key: str = "CRYSTAL_FIELD"):
    bounds_path = REPO_ROOT / 'configs' / bounds_file

    with open(Path(bounds_path), 'r') as f:
        bounds = json.load(f)

    return bounds[key]