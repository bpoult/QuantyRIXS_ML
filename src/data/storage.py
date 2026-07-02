import h5py
import numpy as np
import json
from pathlib import Path
from src.params import CrystalFieldParams

def save_dataset(spectra: np.ndarray, energies: np.ndarray, params: list[CrystalFieldParams], output_path: str, metadata: dict):
    """
    Save a dataset of Quanty simulations to HDF5 format with a companion metadata JSON.

    Parameters:
    -----------
    spectra : np.ndarray, shape (N, n_energy_points)
        Intensity arrays for each simulation.
    energies : np.ndarray, shape (n_energy_points,)
        Shared energy grid across all spectra (eV).
    params : list[CrystalFieldParams]
        Crystal field parameters used for each simulation.
    output_path : str
        Path to save the .h5 file. A companion .json file is saved at the same path.
    metadata : dict
        Additional info to save alongside the dataset (e.g. date, param ranges, Quanty version).
    """

    # Convert to Path object for easier manipulation and check that parent directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # write data in h5py file
    with h5py.File(output_path, "w") as f:
        f.create_dataset("Energies", data=energies)
        f.create_dataset("Spectra", data=spectra)

        # Create folder within h5py for parameter data
        params_grp = f.create_group("Params")
        params_grp.create_dataset("ten_dq_i", data=np.array([p.ten_dq_i for p in params]))
        params_grp.create_dataset("ten_dq_f", data=np.array([p.ten_dq_f for p in params]))

    json_path = output_path.with_suffix(".json")
    with open(json_path, "w") as f:
        json.dump(metadata, f, indent=4)

def load_dataset(input_path: str):
    """
    Load a dataset of Quanty simulations from HDF5 format with metadata.

    Parameters:
    -----------
    input_path : str
        Path to save the .h5 file.

    Returns:
    --------
    spectra : np.ndarray, shape (N, n_energy_points)
        Intensity arrays for each simulation.
    energies : np.ndarray, shape (n_energy_points,)
        Shared energy grid across all spectra (eV).
    params : list[CrystalFieldParams]
        Crystal field parameters reconstructed from the dataset.
    metadata : dict
        Additional info saved alongside the dataset.
    """

    input_path = Path(input_path)

    # Read arrays from HDF5 and reconstruct CrystalFieldParams objects
    with h5py.File(input_path, "r") as f:
        energies = f['Energies'][:]
        spectra = f['Spectra'][:]

        # Load each parameter column then stack into shape (N, 4) for from_array
        ten_dq_i = f['Params']['ten_dq_i'][:]
        ten_dq_f = f['Params']['ten_dq_f'][:]
        
        params_arr = np.stack([ten_dq_i, ten_dq_f], axis=1)  # shape (N, 2 (num of parameters))
        params = [CrystalFieldParams.from_array(params_arr[i]) for i in range(len(params_arr))]

    # Load companion metadata JSON
    json_path = input_path.with_suffix(".json")
    with open(json_path, "r") as f:
        metadata = json.load(f)

    return spectra, energies, params, metadata
