import numpy as np
import logging
import subprocess
import h5py
from src.params import CrystalFieldParams
from src.data import save_simulation
from src.spectra import run_quanty_sim, extract_from_spec, generate_inp_quanty, generate_inp_rixs, build_quanty_dicts, standardize_spectrum
from src.sampling import latin_hypercube_sampling
from src.utils import setup_logger
from pathlib import Path

logger = setup_logger()

PARAMS_SETUP = {
    'atom': 'Co',
    'charge': '6+',
    'edge': 'L',
    'initial_state': 1,
    'rcn_file': '/Users/pierolujanpedreschi/SLAC-Project/QuantyRIXS_ML/RCNparameter.txt',
}

PARAMS_RIXS = {
    'energy_start': 765,
    'energy_end': 800,
    'energy_step': 0.1,
    'loss_start': -6,
    'loss_end': 15,
    'loss_step': 0.05,
    'FWHM_lorentz1': 1.0,
    'FWHM_lorentz1b': 0.7,
    'FWHM_lorentz2': 0.8,
    'Eshift': 0.0,
    'L3_L2_split': 9999,
    'pol': 0,
}

FNAME_QUANTY = 'GS_Oh.inp_quanty'
FNAME_RIXS = 'GS_Oh.inp_rixs'

def generate_dataset(N: int, d: int, output_path: str, lua_file_path: str, l_bounds: np.ndarray, u_bounds: np.ndarray):
    """
    Generate a simulated XAS dataset by running N Quanty simulations with
    randomly sampled ten_dq values, then saving all results to HDF5.

    Parameters:
    -----------
    N : int
        Number of simulations to run.
    d : int
        Dimensions for Latin Hypercube Sampling (# of parameters that will be changed)
    output_path : str
        Directory where simulation folders and final dataset will be saved.
    lua_file_path : str
        Path to the directory containing the Quanty lua script.
    ten_dq_min : float
        Minimum ten_dq value to sample (eV). Default 0.5.
    ten_dq_max : float
        Maximum ten_dq value to sample (eV). Default 5.0.
    """

    # Creates matrix of shape (N, d) with LHS-sampled parameter values — 
    # guarantees even coverage across [l_bounds, u_bounds] with one sample per stratum
    lhs_sample_matrix = latin_hypercube_sampling(N, d, l_bounds, u_bounds)

    dataset_path = Path(output_path) / "dataset.h5"
    start_index = 0

    # check to see if dataset.h5 exists and check last index saved to resume simulations
    if dataset_path.exists():
        with h5py.File(dataset_path, 'r') as f:
            start_index = f['Last Index'][()]
        logger.info(f"Resuming from simulation {start_index}")

    # A fixed array of energy values that every spectrum gets resampled onto
    num_elements = int(round((PARAMS_RIXS['energy_end'] - PARAMS_RIXS['energy_start']) / PARAMS_RIXS['energy_step'])) + 1
    reference_grid = np.linspace(PARAMS_RIXS['energy_start'], PARAMS_RIXS['energy_end'], num=num_elements)

    for i in range(start_index, N):
        # Each simulation gets its own subdirectory to avoid file overwrites
        sim_dir = Path(output_path)/ "simulations" / f"sim_{i:04d}"
        sim_dir.mkdir(parents=True, exist_ok=True)

        # Sample a random parameter values with Latin Hypercube Sampling and wrap it in a CrystalFieldParams object
        ten_dq_i = lhs_sample_matrix[i, 0]
        ten_dq_f = ten_dq_i * lhs_sample_matrix[i, 1]
        cf_params = CrystalFieldParams(ten_dq_i=ten_dq_i, ten_dq_f=ten_dq_f)

        # Merge sampled params with fixed constants into Quanty-ready dicts
        params_i, params_f, params_setup, params_rixs = build_quanty_dicts(
            cf_params, PARAMS_SETUP, PARAMS_RIXS
        )

        # Write Quanty input files into the simulation directory
        generate_inp_quanty(params_i, params_f, params_setup, sim_dir, FNAME_QUANTY)
        generate_inp_rixs(params_rixs, sim_dir, FNAME_RIXS)

        # Run Quanty and capture stdout to find output spectrum filenames
        # sim_result = run_quanty_sim(sim_dir, 'TM_Ledge_spec_job.lua', lua_file_path, timeout=60)

        try:
            sim_result = run_quanty_sim(sim_dir, 'TM_Ledge_spec_job.lua', lua_file_path, timeout=60)
        except subprocess.TimeoutExpired:
            logger.warning(f"[{i+1}/{N}] Simulation timed out — skipping index {i}")
            continue
        except Exception as e:
            logger.error(f"[{i+1}/{N}] Simulation failed: {e} — skipping index {i}")
            continue

        # Parse stdout to find saved .txt spectrum files
        # Ex) 'Saved File: XASisoL3_GS_Oh_1.txt' → 'XASisoL3_GS_Oh_1.txt'
        lines = sim_result.stdout.split('\n')
        saved_files = list(set([line.split()[-1] for line in lines if line.endswith('.txt')]))

         # Check to see if the saved files exist 
        if not saved_files:
            logger.warning(f"[{i+1}/{N}] No output files found — skipping index {i}")
            continue

        # Extract energy grid and intensity array from the first output file
        spec_file = saved_files[0]
        extracted_result = extract_from_spec(folder_path=sim_dir, spec_file=spec_file)

        # Delete .txt spectrum file to save space
        (sim_dir / spec_file).unlink()

        # Store all data into variables to save
        standardized = standardize_spectrum(extracted_result['Energy'], extracted_result['Intensity'], reference_grid)

        # Write or append to .h5 file with new data
        save_simulation(standardized, reference_grid, cf_params, dataset_path, PARAMS_SETUP, i)

        logger.info(f"[{i+1}/{N}] ten_dq_i = {ten_dq_i:.3f} eV ==> ten_dq_f = {ten_dq_f:.3f} eV  —  done")
