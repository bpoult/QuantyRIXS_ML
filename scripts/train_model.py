import argparse
from pathlib import Path
from src.models.model import train_model

if __name__ == "__main__":
    REPO_ROOT = Path(__file__).parent.parent

    parser = argparse.ArgumentParser(description="Train gradient boosting model on XAS dataset")
    parser.add_argument('--dataset_path', type=str, default=str(REPO_ROOT / 'data' / 'medium_dataset' / 's3df_med_dataset.h5'))
    parser.add_argument('--model_path', type=str, default=str(REPO_ROOT / 'models' / 'gradient_boost.joblib'))
    args = parser.parse_args()

    model, x_test, y_test = train_model(args.dataset_path, args.model_path)
    print("Training complete")