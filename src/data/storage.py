import h5py
import numpy as np
import json
import logging
from pathlib import Path
from src.params import CrystalFieldParams

logger = logging.getLogger(__name__)

def save_simulation(spectrum: np.ndarray, energies: np.ndarray, params: CrystalFieldParams, output_path: str, metadata: dict, index: int):
    """
    Write a dataset or append to existing dataset of Quanty simulations to HDF5 format with a companion metadata JSON.

    Parameters:
    -----------
    spectrum : np.ndarray, shape (n_energy_points,)
        Intensity arrays from a simulation.
    energies : np.ndarray, shape (n_energy_points,)
        Shared energy grid across all spectra (eV).
    params : CrystalFieldParams
        Crystal field parameters used in a simulation.
    output_path : str
        Path to save the .h5 file. A companion .json file is saved at the same path.
    metadata : dict
        Additional info to save alongside the dataset (e.g. date, param ranges, Quanty version).
    index : int
        Last simulation index completed by loop
    """
     
    # Convert to Path object for easier manipulation and check that parent directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Append if file already exists, Write file if it does not
    mode = "a" if Path(output_path).exists() else "w"

    # Append or write data in h5py file
    with h5py.File(output_path, mode) as f:
        if mode == 'w':
            f.create_dataset("Last Index", data=index)
            f.create_dataset("Energies", data=energies, maxshape=(None,))
            f.create_dataset("Spectra", data=spectrum.reshape(1, -1), maxshape=(None, energies.size))

            # Create folder within h5py for parameter data
            params_grp = f.create_group("Params")
            params_grp.create_dataset("ten_dq_i", data=np.array([params.ten_dq_i]), maxshape=(None,))
            params_grp.create_dataset("ten_dq_f", data=np.array([params.ten_dq_f]), maxshape=(None,))
            params_grp.create_dataset("Ds_3d_i", data=np.array([params.Ds_3d_i]), maxshape=(None,))
            params_grp.create_dataset("Dt_3d_i", data=np.array([params.Dt_3d_i]), maxshape=(None,))
            params_grp.create_dataset("scalef2_3d3d_i", data=np.array([params.scalef2_3d3d_i]), maxshape=(None,))
            params_grp.create_dataset("scalef4_3d3d_i", data=np.array([params.scalef4_3d3d_i]), maxshape=(None,))
            params_grp.create_dataset("scaleg", data=np.array([params.scaleg]), maxshape=(None,))

        else:
            # Add new row for new data if appending 
            f['Spectra'].resize(f['Spectra'].shape[0] + 1, axis=0)
            f['Params']['ten_dq_i'].resize(f['Params']['ten_dq_i'].shape[0] + 1, axis=0)
            f['Params']['ten_dq_f'].resize(f['Params']['ten_dq_f'].shape[0] + 1, axis=0)
            f['Params']['Ds_3d_i'].resize(f['Params']['Ds_3d_i'].shape[0] + 1, axis=0)
            f['Params']['Dt_3d_i'].resize(f['Params']['Dt_3d_i'].shape[0] + 1, axis=0)
            f['Params']['scalef2_3d3d_i'].resize(f['Params']['scalef2_3d3d_i'].shape[0] + 1, axis=0)
            f['Params']['scalef4_3d3d_i'].resize(f['Params']['scalef4_3d3d_i'].shape[0] + 1, axis=0)
            f['Params']['scaleg'].resize(f['Params']['scaleg'].shape[0] + 1, axis=0)

            # Append data to new row in datasets
            try:
                f['Spectra'][-1] = spectrum

                f['Params']['ten_dq_i'][-1] = params.ten_dq_i
                f['Params']['ten_dq_f'][-1] = params.ten_dq_f
                f['Params']['Ds_3d_i'][-1] = params.Ds_3d_i
                f['Params']['Dt_3d_i'][-1] = params.Dt_3d_i
                f['Params']['scalef2_3d3d_i'][-1] = params.scalef2_3d3d_i
                f['Params']['scalef4_3d3d_i'][-1] = params.scalef4_3d3d_i
                f['Params']['scaleg'][-1] = params.scaleg
                
                f['Last Index'][()] = index
            except Exception as e:
                # Undo the resize by shrinking back
                f['Spectra'].resize(f['Spectra'].shape[0] - 1, axis=0)

                f['Params']['ten_dq_i'].resize(f['Params']['ten_dq_i'].shape[0] - 1, axis=0)
                f['Params']['ten_dq_f'].resize(f['Params']['ten_dq_f'].shape[0] - 1, axis=0)
                f['Params']['Ds_3d_i'].resize(f['Params']['Ds_3d_i'].shape[0] - 1, axis=0)
                f['Params']['Dt_3d_i'].resize(f['Params']['Dt_3d_i'].shape[0] - 1, axis=0)
                f['Params']['scalef2_3d3d_i'].resize(f['Params']['scalef2_3d3d_i'].shape[0] - 1, axis=0)
                f['Params']['scalef4_3d3d_i'].resize(f['Params']['scalef4_3d3d_i'].shape[0] - 1, axis=0)
                f['Params']['scaleg'].resize(f['Params']['scaleg'].shape[0] - 1, axis=0)


                logger.error(f"[{ index + 1 }] Simulation failed: { e } — skipping index { index }")
                raise RuntimeError(f"Failed to append simulation with index: { index }. Error: { e }")

        # Only write metadata file once on write as it will remain constant
        if mode == "w":
            json_path = output_path.with_suffix(".json")
            with open(json_path, "w") as json_file:
                json.dump(metadata, json_file, indent=4)


def load_dataset(dataset_path: str):
    """
    Load a dataset of Quanty simulations from HDF5 format with metadata.

    Parameters:
    -----------
    input_path : str
        Path to open the .h5 file.

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
    index : int
        Last simulation index completed by loop
    """

    dataset_path = Path(dataset_path)

    # Read arrays from HDF5 and reconstruct CrystalFieldParams objects
    with h5py.File(dataset_path, "r") as f:
        index = f['Last Index']
        energies = f['Energies'][:]
        spectra = f['Spectra'][:]

        # Load each parameter column then stack into shape (N, 4) for from_array
        ten_dq_i = f['Params']['ten_dq_i'][:]
        ten_dq_f = f['Params']['ten_dq_f'][:]
        Ds_3d_i = f['Params']['Ds_3d_i'][:]
        Dt_3d_i = f['Params']['Dt_3d_i'][:]
        scalef2_3d3d_i = f['Params'][:]
        scalef4_3d3d_i = f['Params'][:]
        scaleg = f['Params']['scaleg'][:]
        
        params_arr = np.stack([ten_dq_i, ten_dq_f, Ds_3d_i, Dt_3d_i, scalef2_3d3d_i, scalef4_3d3d_i, scaleg], axis=1)  # shape (N, d (num of parameters))
        params = [CrystalFieldParams.from_array(params_arr[i]) for i in range(len(params_arr))]

    # Load companion metadata JSON
    json_path = dataset_path.with_suffix(".json")
    with open(json_path, "r") as f:
        metadata = json.load(f)

    return spectra, energies, params, metadata, index
