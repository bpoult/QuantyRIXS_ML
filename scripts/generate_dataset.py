import numpy as np
import subprocess
import h5py
import argparse
from src.params import CrystalFieldParams
from src.data import save_simulation
from src.spectra import run_quanty_sim, extract_from_spec, generate_inp_quanty, generate_inp_quanty_CT, generate_inp_rixs, build_quanty_dicts, standardize_spectrum
from src.sampling import latin_hypercube_sampling
from src.utils import setup_logger, load_config, load_bounds
from pathlib import Path

logger = setup_logger()
REPO_ROOT = Path(__file__).parent.parent
FNAME_QUANTY = 'GS_Oh.inp_quanty'
FNAME_RIXS = 'GS_Oh.inp_rixs'

def generate_dataset(N: int, 
                     start_index: int, 
                     end_index: int, 
                     mode: str,
                     output_path: str, 
                     lua_file_path: str, 
                     PARAMS_SETUP: dict, 
                     PARAMS_RIXS: dict):
    """
    Generate a simulated XAS dataset by running N Quanty simulations with
    randomly sampled ten_dq values, then saving all results to HDF5.

    Parameters:
    -----------
    N : int
        Total dataset size.
    start_index: int
        First index of the batch
    end_index : int
        Last index of the batch
    mode: str
        Determines whether dataset will use Crystal Field Params or CF + charge transfer params
    output_path : str
        Directory where simulation folders and final dataset will be saved.
    lua_file_path : str
        Path to the directory containing the Quanty lua script.
    PARAMS_SETUP : dict
        Setup information for the specific complex, used for metadata
    PARAMS_RIXS : dict
        RIXS information for specfic complex and spectrum type
    """

    # Load boundaries from configs directory
    cf_bounds = load_bounds('param_bounds.json', key='CRYSTAL_FIELD')
    ct_bounds = load_bounds('param_bounds.json', key='CHARGE_TRANSFER') 

    if mode == 'CT':
        l_bounds = cf_bounds['LOWER_BOUNDS'] + ct_bounds['LOWER_BOUNDS']
        u_bounds = cf_bounds['UPPER_BOUNDS'] + ct_bounds['UPPER_BOUNDS']
    else:
        l_bounds = cf_bounds['LOWER_BOUNDS']
        u_bounds = cf_bounds['UPPER_BOUNDS']

    d = len(l_bounds)  #  7 or 17

    # Creates matrix of shape (N, d) with LHS-sampled parameter values — 
    # guarantees even coverage across [l_bounds, u_bounds] with one sample per stratum
    lhs_sample_matrix = latin_hypercube_sampling(N, d, l_bounds, u_bounds)

    # check to see if dataset.h5 exists and check last index saved to resume simulations
    dataset_path = Path(output_path) / "dataset.h5"
    if dataset_path.exists():
        with h5py.File(dataset_path, 'r') as f:
            # Read the last saved simulation index and start from the next one
            # e.g. if last index was 9 (10 simulations done), start_index = 10
            # range(10, 10) is empty — no duplicates if N hasn't changed
            # range(10, 20) resumes from sim 10 if N was increased to 20
            start_index =  start_index + f['Last Index'][()] + 1
            if start_index == N:
                logger.info(f"Simulations are up to date. Last Index = {start_index}")
            else:
                logger.info(f"Resuming from simulation {start_index}")

    # A fixed array of energy values that every spectrum gets resampled onto
    num_elements = int(round((PARAMS_RIXS['energy_end'] - PARAMS_RIXS['energy_start']) / PARAMS_RIXS['energy_step'])) + 1
    reference_grid = np.linspace(PARAMS_RIXS['energy_start'], PARAMS_RIXS['energy_end'], num=num_elements)

    for i in range(start_index, end_index):
        # Each simulation gets its own subdirectory to avoid file overwrites
        sim_dir = Path(output_path) / "working_dir"
        sim_dir.mkdir(parents=True, exist_ok=True)

        # Sample a random parameter values with Latin Hypercube Sampling and wrap it in a CrystalFieldParams object
        # CF parameters (indices 0-6)
        ten_dq_i = lhs_sample_matrix[i, 0]
        ten_dq_f = ten_dq_i * lhs_sample_matrix[i, 1]
        Ds_3d_i = lhs_sample_matrix[i, 2]
        Dt_3d_i = lhs_sample_matrix[i, 3]
        scalef2_3d3d_i = lhs_sample_matrix[i, 4]
        scalef4_3d3d_i = lhs_sample_matrix[i, 5]
        scaleg = lhs_sample_matrix[i, 6]

        # CT initial state (indices 7-11)
        if mode == 'CT':
            Delta_3d_L1_i = lhs_sample_matrix[i, 7]
            Veg_3d_L1_i = lhs_sample_matrix[i, 8]
            Vt2g_3d_L1_i = lhs_sample_matrix[i, 9]
            Delta_3d_L2_i = lhs_sample_matrix[i, 10]
            Vt2g_3d_L2_i = lhs_sample_matrix[i, 11]

            # CT final state derived from offsets/reductions (indices 12-16)
            Delta_3d_L1_f = Delta_3d_L1_i + lhs_sample_matrix[i, 12]
            Veg_3d_L1_f = Veg_3d_L1_i * lhs_sample_matrix[i, 13]
            Vt2g_3d_L1_f = Vt2g_3d_L1_i * lhs_sample_matrix[i, 14]
            Delta_3d_L2_f = Delta_3d_L2_i + lhs_sample_matrix[i, 15]
            Vt2g_3d_L2_f = Vt2g_3d_L2_i * lhs_sample_matrix[i, 16]
        else:
            Delta_3d_L1_i = 0
            Veg_3d_L1_i = 0
            Vt2g_3d_L1_i = 0
            Delta_3d_L2_i = 0
            Vt2g_3d_L2_i = 0
            Delta_3d_L1_f = 0
            Veg_3d_L1_f = 0
            Vt2g_3d_L1_f = 0
            Delta_3d_L2_f = 0
            Vt2g_3d_L2_f = 0

        cf_params = CrystalFieldParams(
            ten_dq_i=ten_dq_i, ten_dq_f=ten_dq_f,
            Ds_3d_i=Ds_3d_i, Dt_3d_i=Dt_3d_i,
            scalef2_3d3d_i=scalef2_3d3d_i, scalef4_3d3d_i=scalef4_3d3d_i,
            scaleg=scaleg,
            Delta_3d_L1_i=Delta_3d_L1_i, Veg_3d_L1_i=Veg_3d_L1_i,
            Vt2g_3d_L1_i=Vt2g_3d_L1_i, Delta_3d_L2_i=Delta_3d_L2_i,
            Vt2g_3d_L2_i=Vt2g_3d_L2_i,
            Delta_3d_L1_f=Delta_3d_L1_f, Veg_3d_L1_f=Veg_3d_L1_f,
            Vt2g_3d_L1_f=Vt2g_3d_L1_f, Delta_3d_L2_f=Delta_3d_L2_f,
            Vt2g_3d_L2_f=Vt2g_3d_L2_f
        )

        # Merge sampled params with fixed constants into Quanty-ready dicts
        params_i, params_f, params_setup, params_rixs = build_quanty_dicts(
            cf_params, PARAMS_SETUP, PARAMS_RIXS
        )

        # Write Quanty input files into the simulation directory
        if mode == 'CT':
            generate_inp_quanty_CT(params_i, params_f, params_setup, sim_dir, FNAME_QUANTY)
        else:
            generate_inp_quanty(params_i, params_f, params_setup, sim_dir, FNAME_QUANTY)
        generate_inp_rixs(params_rixs, sim_dir, FNAME_RIXS)

        # Run Quanty and capture stdout to find output spectrum filenames
        try:
            lua_file = 'TM_Ledge_CT_spec_job.lua' if mode == 'CT' else 'TM_Ledge_spec_job.lua'
            sim_result = run_quanty_sim(sim_dir, lua_file, lua_file_path, timeout=60)
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
        extracted_result = extract_from_spec(sim_dir / spec_file)

        # Store all data into variables to save
        standardized = standardize_spectrum(extracted_result['Energy'], extracted_result['Intensity'], reference_grid)

        # Write or append to .h5 file with new data
        local_index = i - start_index
        save_simulation(standardized, reference_grid, cf_params, dataset_path, PARAMS_SETUP, local_index)

        log_msg = (
            f"[{i+1}/{N}] done — "
            f"ten_dq_i={ten_dq_i:.3f} | "
            f"ten_dq_f={ten_dq_f:.3f} | "
            f"Ds_3d_i={Ds_3d_i:.3f} | "
            f"Dt_3d_i={Dt_3d_i:.3f} | "
            f"scalef2={scalef2_3d3d_i:.3f} | "
            f"scalef4={scalef4_3d3d_i:.3f} | "
            f"scaleg={scaleg:.3f}"
        )

        if mode == 'CT':
            log_msg += (
                f" | Delta_L1_i={Delta_3d_L1_i:.3f} | "
                f"Veg_L1_i={Veg_3d_L1_i:.3f} | "
                f"Vt2g_L1_i={Vt2g_3d_L1_i:.3f} | "
                f"Delta_L2_i={Delta_3d_L2_i:.3f} | "
                f"Vt2g_L2_i={Vt2g_3d_L2_i:.3f}"
            )

        logger.info(log_msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate XAS simulation dataset")
    parser.add_argument('--N', type=int, default=2000)
    parser.add_argument('--output_path', type=str, default=str(REPO_ROOT / 'data'))
    parser.add_argument('--lua_file_path', type=str, default=str(REPO_ROOT))
    parser.add_argument('--complex', type=str, default='co_terpy')
    parser.add_argument('--spectrum_type', type=str, default='L3')
    parser.add_argument('--initial_state', type=str, default='1')
    parser.add_argument('--batch_index', type=int, default=0)
    parser.add_argument('--batch_size', type=int, default=500)
    parser.add_argument('--mode', type=str, default='CF', choices=['CF', 'CT'])
    args = parser.parse_args()

    start_index = args.batch_index * args.batch_size
    end_index = start_index + args.batch_size

    complex_spec_type = f"{args.complex}_{args.spectrum_type}_state{args.initial_state}_{args.mode}"
    batch_output_path = Path(args.output_path) / f"{complex_spec_type}_data" / f"batch_{args.batch_index:04d}"

    config_file = f'{complex_spec_type}_params.json'
    config = load_config(config_file)

    PARAMS_SETUP = config['PARAMS_SETUP']
    PARAMS_RIXS = config['PARAMS_RIXS']
    
    generate_dataset(args.N, start_index, end_index, args.mode, batch_output_path, args.lua_file_path, PARAMS_SETUP, PARAMS_RIXS)

   
