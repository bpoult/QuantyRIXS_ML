import numpy as np
from src.params import CrystalFieldParams
from src.data import save_dataset
from src.spectra import run_quanty_sim, extract_from_spec, generate_inp_quanty, generate_inp_rixs, build_quanty_dicts
from pathlib import Path

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

def generate_dataset(N: int, output_path: str, lua_file_path: str, ten_dq_min: float = 0.5, ten_dq_max: float = 5.0):
    """
    Generate a simulated XAS dataset by running N Quanty simulations with
    randomly sampled ten_dq values, then saving all results to HDF5.

    Parameters:
    -----------
    N : int
        Number of simulations to run.
    output_path : str
        Directory where simulation folders and final dataset will be saved.
    lua_file_path : str
        Path to the directory containing the Quanty lua script.
    ten_dq_min : float
        Minimum ten_dq value to sample (eV). Default 0.5.
    ten_dq_max : float
        Maximum ten_dq value to sample (eV). Default 5.0.
    """

    rng = np.random.default_rng()

    all_spectra = []    # collects intensity arrays, one per simulation
    all_params = []     # collects CrystalFieldParams objects, one per simulation
    energies = None     # shared energy grid — captured from first simulation

    for i in range(N):
        # Each simulation gets its own subdirectory to avoid file overwrites
        sim_dir = Path(output_path)/ "simulations" / f"sim_{i:04d}"
        sim_dir.mkdir(parents=True, exist_ok=True)

        # Sample a random ten_dq and wrap it in a CrystalFieldParams object
        ten_dq_i = rng.uniform(low=ten_dq_min, high=ten_dq_max)
        ten_dq_f = ten_dq_i * (1 - rng.uniform(low=0, high=0.25))
        cf_params = CrystalFieldParams(ten_dq_i=ten_dq_i, ten_dq_f=ten_dq_f)

        # Merge sampled params with fixed constants into Quanty-ready dicts
        params_i, params_f, params_setup, params_rixs = build_quanty_dicts(
            cf_params, PARAMS_SETUP, PARAMS_RIXS
        )

        # Write Quanty input files into the simulation directory
        generate_inp_quanty(params_i, params_f, params_setup, sim_dir, FNAME_QUANTY)
        generate_inp_rixs(params_rixs, sim_dir, FNAME_RIXS)

        # Run Quanty and capture stdout to find output spectrum filenames
        sim_result = run_quanty_sim(sim_dir, 'TM_Ledge_spec_job.lua', lua_file_path)

        # Parse stdout to find saved .txt spectrum files
        # Ex) 'Saved File: XASisoL3_GS_Oh_1.txt' → 'XASisoL3_GS_Oh_1.txt'
        lines = sim_result.stdout.split('\n')
        saved_files = list(set([line.split()[-1] for line in lines if line.endswith('.txt')]))

        # Extract energy grid and intensity array from the first output file
        spec_file = saved_files[0]
        extract_result = extract_from_spec(folder_path=sim_dir, spec_file=spec_file)

        # Delete .txt spectrum file to save space
        (sim_dir / spec_file).unlink()

        # Capture energy grid once — it is identical across all simulations
        if energies is None:
            energies = extract_result['Energy']

        all_spectra.append(extract_result['Intensity'])
        all_params.append(cf_params)
        print(f"[{i+1}/{N}] ten_dq_i={ten_dq_i:.3f} eV ==> ten_dq_f={ten_dq_f:.3f} eV— done")

    # Stack intensity arrays into a 2D array of shape (N, n_energy_points)
    spectra_array = np.stack(all_spectra)

    # Save the full dataset to HDF5 + companion metadata JSON
    save_dataset(spectra_array, energies, all_params, Path(output_path) / "dataset.h5", PARAMS_SETUP)