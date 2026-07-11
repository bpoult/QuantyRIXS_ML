from pathlib import Path
from src.models.train import train_model

REPO_ROOT = Path(__file__).parent.parent
dataset_path = REPO_ROOT / 'data' / 'medium_dataset' / 'dataset.h5'
model_path = REPO_ROOT / 'models' / 'gradient_boost.joblib'

model, x_test, y_test = train_model(str(dataset_path), str(model_path))
print("Training complete")