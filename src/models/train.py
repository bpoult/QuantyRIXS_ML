import numpy as np

from joblib import dump, load
from pathlib import Path
from src.data import load_dataset
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor

def train_model(dataset_path: str, model_path: str = 'models/gradient_boost.joblib'):
    """
    Loads a simulated XAS dataset, splits it into training and test sets,
    trains a MultiOutputRegressor wrapping GradientBoostingRegressor to predict
    crystal field parameters from spectra, and saves the trained model to disk.

    Parameters:
    -----------
    dataset_path : str
        Path to the dataset .h5 file.
    model_path : str
        Path where the trained model will be saved. Default: 'models/gradient_boost.joblib'

    Returns:
    --------
    model : MultiOutputRegressor
        Trained model that maps spectra to crystal field parameters.
    x_test : np.ndarray, shape (N_test, n_energy_points)
        Spectra held out for evaluation.
    y_test : np.ndarray, shape (N_test, n_params)
        True parameter values for the test spectra.
    """

    spectra, _, params, _, _ = load_dataset(dataset_path)
    
    x = spectra
    # convert array of CrystalFieldParams to a numpy array of parameter values with shape (N, d: num of params)
    y = np.array([p.to_array() for p in params])
    
    # Set test size to 20% of the dataset, random_state/seed to 42 for reproducibility
    x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42)

    # GradientBoostingRegressor only handles 1 output at a time
    base_model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=4
    )

    # MultiOutputRegressor splits y data into d separate targets, and trains one
    # GradientBoostingRegressor for each target
    model = MultiOutputRegressor(base_model)
    model.fit(x_train, y_train)

    # Ensure model directory exists and save trained model to disk
    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    dump(model, model_path)

    return model, x_test, y_test