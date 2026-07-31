import argparse
from pathlib import Path
from src.models.model import train_model

if __name__ == "__main__":
    REPO_ROOT = Path(__file__).parent.parent

    parser = argparse.ArgumentParser(description="Train gradient boosting model on XAS dataset")
    parser.add_argument('--complex', type=str, default='co_terpy')
    parser.add_argument('--spectrum_type', type=str, default='L3')
    parser.add_argument('--initial_state', type=str, default='1')
    args = parser.parse_args()

    complex_spec_type = f"{args.complex}_{args.spectrum_type}_state{args.initial_state}"

    dataset_path = REPO_ROOT / 'data' / f'{complex_spec_type}_data' / 'dataset.h5'
    model_path = REPO_ROOT / 'models' / f'gradient_boost_{complex_spec_type}.joblib'

    model, x_test, y_test = train_model(dataset_path, model_path)
    print("Training complete")