import numpy as np

from joblib import dump, load
from src.data import load_dataset
from sklearn.model_selection import train_test_split

def train_model(dataset_path):
    spectra, _, params, _, _ = load_dataset(dataset_path)
    
    x = spectra
    y = np.array([p.to_array() for p in params])



