import h5py
import json
import argparse
import numpy as np
from pathlib import Path
from src.utils import setup_logger

logger = setup_logger()
REPO_ROOT = Path(__file__).parent.parent

def merge_datasets(data_path: Path, num_batches: int, complex_spec_type: str):
    """
    Merge all batch HDF5 files into one final dataset and generate reference spectrum.

    Parameters:
    -----------
    data_path : Path
        Directory containing batch_0000/, batch_0001/, etc.
    num_batches : int
        Number of batches to merge.
    complex_spec_type : str
        e.g. 'co_terpy_L3L2' — used for naming output files.
    """
    all_spectra = []
    all_params = []
    energies = None
    metadata = None

    # Load each batch and accumulate arrays
    for batch_idx in range(num_batches):
        batch_path = data_path / f"batch_{batch_idx:04d}" / "dataset.h5"

        if not batch_path.exists():
            logger.warning(f"Batch {batch_idx} not found at {batch_path} — skipping")
            continue

        with h5py.File(batch_path, 'r') as f:
            all_spectra.append(f['Spectra'][:])
            all_params.append(f['Params'][:])
            if energies is None:
                energies = f['Energies'][:]

        # Load companion metadata JSON from first batch only
        if metadata is None:
            json_path = batch_path.with_suffix('.json')
            if json_path.exists():
                with open(json_path, 'r') as f:
                    metadata = json.load(f)

        logger.info(f"Loaded batch {batch_idx}")

    # Stack all batches into single arrays
    spectra = np.concatenate(all_spectra, axis=0)
    params = np.concatenate(all_params, axis=0)

    logger.info(f"Total simulations merged: {spectra.shape[0]}")

    # Save merged dataset to HDF5
    output_path = data_path / "dataset.h5"
    with h5py.File(output_path, 'w') as f:
        f.create_dataset("Energies", data=energies)
        f.create_dataset("Spectra", data=spectra)
        f.create_dataset("Last Index", data=spectra.shape[0] - 1)
        f.create_dataset("Params", data=params)


    # Save companion metadata JSON
    if metadata is not None:
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=4)

    # Generate and save reference spectrum
    reference_spectrum = np.mean(spectra, axis=0)
    reference_path = data_path / f'{complex_spec_type}_reference_spectrum.npy'
    np.save(str(reference_path), reference_spectrum)
    logger.info(f"Reference spectrum saved to {reference_path}")
    logger.info(f"Merged dataset saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge batch HDF5 datasets into one")
    parser.add_argument('--data_path', type=str, default=str(REPO_ROOT / 'data'))
    parser.add_argument('--complex', type=str, default='co_terpy')
    parser.add_argument('--spectrum_type', type=str, default='L3')
    parser.add_argument('--initial_state', type=str, default='1')
    parser.add_argument('--num_batches', type=int, default=10)
    parser.add_argument('--mode', type=str, default='CF', choices=['CF', 'CT'])
    args = parser.parse_args()

    complex_spec_type = f"{args.complex}_{args.spectrum_type}_state{args.initial_state}_{args.mode}"
    data_path = Path(args.data_path) / f"{complex_spec_type}_data"

    merge_datasets(data_path, args.num_batches, complex_spec_type)