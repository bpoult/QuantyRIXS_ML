import numpy as np
import subprocess
import h5py
import argparse
from src.params import CrystalFieldParams
from src.data import save_simulation
from src.spectra import run_quanty_sim, extract_from_spec, generate_inp_quanty, generate_inp_rixs, build_quanty_dicts, standardize_spectrum
from src.sampling import latin_hypercube_sampling
from src.utils import setup_logger, load_config
from pathlib import Path

logger = setup_logger()
REPO_ROOT = Path(__file__).parent.parent
FNAME_QUANTY = 'GS_Oh.inp_quanty'
FNAME_RIXS = 'GS_Oh.inp_rixs'

def generate_dataset(N: int, d: int, output_path: str, lua_file_path: str, l_bounds: np.ndarray, u_bounds: np.ndarray, PARAMS_SETUP: dict, PARAMS_RIXS: dict):
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
    l_bounds : list of float
        Lower bounds for each sampled parameter, length d.
    u_bounds : list of float
        Upper bounds for each sampled parameter, length d.
    """

    # Creates matrix of shape (N, d) with LHS-sampled parameter values — 
    # guarantees even coverage across [l_bounds, u_bounds] with one sample per stratum
    lhs_sample_matrix = latin_hypercube_sampling(N, d, l_bounds, u_bounds)

    dataset_path = Path(output_path) / "dataset.h5"
    start_index = 0

    # check to see if dataset.h5 exists and check last index saved to resume simulations
    if dataset_path.exists():
        with h5py.File(dataset_path, 'r') as f:
            # Read the last saved simulation index and start from the next one
            # e.g. if last index was 9 (10 simulations done), start_index = 10
            # range(10, 10) is empty — no duplicates if N hasn't changed
            # range(10, 20) resumes from sim 10 if N was increased to 20
            start_index = f['Last Index'][()] + 1
            if start_index == N:
                logger.info(f"Simulations are up to date. Last Index = {start_index}")
            else:
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
        # print(f'lines: {lines}')
        saved_files = list(set([line.split()[-1] for line in lines if line.endswith('.txt')]))
        # print(f'saved_files: {saved_files}')

         # Check to see if the saved files exist 
        if not saved_files:
            logger.warning(f"[{i+1}/{N}] No output files found — skipping index {i}")
            continue

        # Extract energy grid and intensity array from the first output file
        spec_file = saved_files[0]
        # print(f'spec file: {spec_file}')
        extracted_result = extract_from_spec(sim_dir / spec_file)
        # print(f'extracted result: {extracted_result}')
        # print(f'extracted result size: {extracted_result['Intensity'].size}')


        # Delete .txt spectrum file to save space
        # (sim_dir / spec_file).unlink()

        # Store all data into variables to save
        standardized = standardize_spectrum(extracted_result['Energy'], extracted_result['Intensity'], reference_grid)

        # Write or append to .h5 file with new data
        save_simulation(standardized, reference_grid, cf_params, dataset_path, PARAMS_SETUP, i)

        logger.info(f"[{i+1}/{N}] ten_dq_i = {ten_dq_i:.3f} eV ==> ten_dq_f = {ten_dq_f:.3f} eV  —  done")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate XAS simulation dataset")
    parser.add_argument('--N', type=int, default=2000)
    parser.add_argument('--d', type=int, default=2)
    parser.add_argument('--output_path', type=str, default=str(REPO_ROOT / 'data' / 'co_terpy_L3_data'))
    parser.add_argument('--lua_file_path', type=str, default=str(REPO_ROOT))
    parser.add_argument('--l_bounds', type=float, nargs='+', default=[0.5, 0.75])
    parser.add_argument('--u_bounds', type=float, nargs='+', default=[5.0, 1.0])
    parser.add_argument('--complex', type=str, default='co_terpy')
    parser.add_argument('--spectrum_type', type=str, default='L3')
    args = parser.parse_args()

    complex_spec_type = f'{args.complex}_{args.spectrum_type}'
    output_path = args.output_path / f'{complex_spec_type}_data'

    config_file = f'{complex_spec_type}_params.json'
    config = load_config(config_file)
    PARAMS_SETUP = config['PARAMS_SETUP']
    PARAMS_RIXS = config['PARAMS_RIXS']
    generate_dataset(args.N, args.d, output_path, args.lua_file_path, args.l_bounds, args.u_bounds, PARAMS_SETUP, PARAMS_RIXS)

    # Generate reference spectrum from completed dataset
    logger.info("Generating reference spectrum from dataset...")
    with h5py.File(Path(output_path) / 'dataset.h5', 'r') as f:
        spectra = f['Spectra'][:]

    reference_spectrum = np.mean(spectra, axis=0)

    # Ex.) REPO_ROOT/data/co_terpy_L3L2_reference_spectrum.npy
    reference_path = output_path / f'{complex_spec_type}_reference_spectrum.npy'

    np.save(str(reference_path), reference_spectrum)
    logger.info(f"Reference spectrum saved to {reference_path}")
