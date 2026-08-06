import subprocess
import os
import shutil
import numpy as np
from pathlib import Path
from parse_rcn import parse_rcn_parameters
from src.params import CrystalFieldParams


def run_quanty_sim(folder_path, lua_file, lua_file_path=None, timeout=None):
    """
    Run X-ray absorption spectrum simulation from specified folder.
    
    Parameters:
    -----------
    folder_path : str or Path
        Path to folder containing .lua, .inp_quanty, and .inp_rixs files
    lua_file : str
        Name of the lua file to execute (default: "greenMLCT_Co3d6_D4h_RCN_conf_job.lua")
    lua_file_path : str or Path, optional
        Directory containing the lua file to copy into folder_path. The lua_file name will be appended.
        If None, assumes lua_file is already in folder_path
    timeout : int, optional
        Maximum time in seconds to wait for simulation (default: None, no timeout)
    
    Returns:
    --------
    result : subprocess.CompletedProcess
        Contains return code, stdout, stderr
    
    Raises:
    -------
    FileNotFoundError : if folder or lua file doesn't exist
    subprocess.TimeoutExpired : if simulation exceeds timeout
    """
    
    # Convert to Path object for easier manipulation
    folder_path = Path(folder_path)
    
    # Verify folder exists
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    
    # If lua_file_path is provided, copy the file to folder_path
    if lua_file_path is not None:
        lua_file_path = Path(lua_file_path)
        
        
        # Append lua_file name to the directory path
        source_file = lua_file_path / lua_file
        
        if not source_file.exists():
            raise FileNotFoundError(f"Source lua file not found: {source_file}")

        
        destination = folder_path / lua_file
        shutil.copy2(source_file, destination)

        with open(destination, 'r') as f:
            lua_content = f.read()

        # Find existing configuration files in destination folder
        inp_quanty = [f for f in os.listdir(folder_path) if f.endswith('.inp_quanty')]
        inp_rixs = [f for f in os.listdir(folder_path) if f.endswith('.inp_rixs')]
        
        # Append two variables at the top of Lua file content with the String value of the names of the config files
        lua_content = (
            f'target_file_quanty = "{inp_quanty[0] if inp_quanty else ""}"\n'
            f'target_file_rixs = "{inp_rixs[0] if inp_rixs else ""}"\n'
        ) + lua_content

        # Write into Lua file
        with open(destination, 'w') as f:
            f.write(lua_content)
    
    # Verify lua file exists in folder_path
    lua_path = folder_path / lua_file
    if not lua_path.exists():
        raise FileNotFoundError(f"Lua file not found: {lua_path}")
    
    # Store current directory to return to it later
    original_dir = os.getcwd()
    
    try:
        # Change to simulation directory
        os.chdir(folder_path)
        
        # Build command - REPLACE THIS with your actual command
        command = f"Quanty {lua_file}"
        if lua_file:
            # Run simulation
            print("looking for result")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                # timeout=timeout
            )
        # Check if simulation succeeded
        if result.returncode != 0:
            print(f"Warning: Simulation returned non-zero exit code: {result.returncode}")
            print(f"STDERR: {result.stderr}")
        
        return result
        
    finally:
        # Always return to original directory
        os.chdir(original_dir)


def extract_from_spec(spec_path):
    """
    Take the Quanty XAS output data then extract the Energy and Intensity Column

    Parameters:
    -----------
    spec_path : str
        Path to the file the Quanty output .txt to parse
    
    Returns:
    --------
    result : {'Energy': energy, 'Intensity': intensity}
        Dictionary that contains 2 np.arrays as the values
    
    Raises:
    -------
    FileNotFoundError : if folder or output file doesn't exist
    """

    #Convert to Path object for easier manipulation
    spec_path = Path(spec_path)
    
    # Verify spec_file exists in folder
    if not spec_path.exists():
        raise FileNotFoundError(f"File not found: {spec_path}")
    
    # assign data var with numerical data from text file, skip first 5 rows of header lines
    data = np.loadtxt(spec_path, skiprows=5)

    energy = data[:, 0]
    intensity = data[:, 2]

    return {'Energy': energy, 'Intensity': intensity}

def extract_from_experiment(experiment_path):
    """
    Take the Experimental Spectrum output data then extract the Energy and Intensity Column

    Parameters:
    -----------
    experiment_path : str or Path
        Path to the experiment output .txt file to parse
    
    Returns:
    --------
    result : {'Energy': energy, 'Intensity': intensity}
        Dictionary that contains 2 np.arrays as the values
    
    Raises:
    -------
    FileNotFoundError : if folder or output file doesn't exist
    """

    #Convert to Path object for easier manipulation
    experiment_path = Path(experiment_path)
    
    # Verify spec_file exists in folder
    if not experiment_path.exists():
        raise FileNotFoundError(f"File not found: {experiment_path}")
    
    # assign data var with numerical data from text file, skip first 5 rows of header lines
    data = np.loadtxt(experiment_path)

    energy = data[:, 0]
    intensity = data[:, 1]


    return {'Energy': energy, 'Intensity': intensity}

def build_quanty_dicts(params: CrystalFieldParams, params_setup: dict, params_rixs: dict=None):
    if params.E_2p is None:
        params.E_2p = params_setup['E_2p']
        
    params_i = {
        'NPsi_i': params.NPsi_i,
        'tenDq_3d_i': params.ten_dq_i,
        'Ds_3d_i': params.Ds_3d_i,
        'Dt_3d_i': params.Dt_3d_i,
        'scalef2_3d3d_i': params.scalef2_3d3d_i,
        'scalef4_3d3d_i': params.scalef4_3d3d_i,
        'scale_3dSOC_i': params.scale_3dSOC_i,
        'U_3d_3d_i': params.U_3d_3d_i,
        # CT parameters - initial state
        'tenDq_L1_i': params.ten_dq_L1_i,
        'Delta_3d_L1_i': params.Delta_3d_L1_i,
        'Veg_3d_L1_i': params.Veg_3d_L1_i,
        'Vt2g_3d_L1_i': params.Vt2g_3d_L1_i,
        'tenDq_L2_i': params.ten_dq_L2_i,
        'Delta_3d_L2_i': params.Delta_3d_L2_i,
        'Veg_3d_L2_i': params.Veg_3d_L2_i,
        'Vt2g_3d_L2_i': params.Vt2g_3d_L2_i,
    }

    params_f = {
        'NPsi_f': params.NPsi_f,
        'tenDq_3d_f': params.ten_dq_f,
        'Ds_3d_f': params.Ds_3d_f,
        'Dt_3d_f': params.Dt_3d_f,
        'scalef2_3d3d_f': params.scalef2_3d3d_f,
        'scalef4_3d3d_f': params.scalef4_3d3d_f,
        'scale_3dSOC_f': params.scale_3dSOC_f,
        'U_3d_3d_f': params.U_3d_3d_f,
        'U_2p_3d_f': params.U_2p_3d_f,
        'scalef2_2p3d': params.scalef2_2p3d,
        'scaleg': params.scaleg,
        'scale_2pSOC': params.scale_2pSOC,
        'E_2p': params.E_2p,
        # CT parameters - final state
        'tenDq_L1_f': params.ten_dq_L1_f,
        'Delta_3d_L1_f': params.Delta_3d_L1_f,
        'Veg_3d_L1_f': params.Veg_3d_L1_f,
        'Vt2g_3d_L1_f': params.Vt2g_3d_L1_f,
        'tenDq_L2_f': params.ten_dq_L2_f,
        'Delta_3d_L2_f': params.Delta_3d_L2_f,
        'Veg_3d_L2_f': params.Veg_3d_L2_f,
        'Vt2g_3d_L2_f': params.Vt2g_3d_L2_f,
    }

    return params_i, params_f, params_setup, params_rixs

def generate_inp_quanty(parameters_i, parameters_f, parameters_setup, output_path, fname):
    """
    Generate .inp_quanty file with specified parameters.

    Parameters:
    -----------
    parameters_i : dict
        Initial state parameters. Expected keys:
        - NPsi_i
        - tenDq_3d_i
        - Ds_3d_i
        - Dt_3d_i
        - scalef2_3d3d_i
        - scalef4_3d3d_i
        - scale_3dSOC_i
        - U_3d_3d_i

    parameters_f : dict
        Final state parameters. Expected keys:
        - NPsi_f
        - tenDq_3d_f
        - Ds_3d_f
        - Dt_3d_f
        - scalef2_3d3d_f
        - scalef4_3d3d_f
        - scale_3dSOC_f
        - U_3d_3d_f
        - U_2p_3d_f
        - scalef2_2p3d
        - scaleg
        - scale_2pSOC
        - E_2p

    parameters_setup : dict
        System identification and setup. Expected keys:
        - atom         : element symbol, e.g. 'Co'
        - charge       : charge string,  e.g. '3+'
        - edge         : absorption edge, e.g. 'L' (only 'L' currently supported)
        - initial_state: integer >= 1; 1 = ground state, higher = excited states
        - rcn_file     : path to RCNparameter.txt

        The atom/charge/edge combination is used to look up the 10 bare atomic
        Slater integrals and SOC constants from RCNparameter.txt.  These values
        are written to the file automatically and should not be edited by hand.

    output_path : str or Path
        Path where the .inp_quanty file should be written
        (can be a directory or full file path)

    fname : str
        Filename for the output file

    Returns:
    --------
    output_file : Path
        Full path to the generated file
    """

    # Convert to Path object
    output_path = Path(output_path)

    # If output_path is a directory, append filename
    if output_path.is_dir():
        output_file = output_path / fname
    else:
        output_file = output_path

    # Create parent directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Look up atomic RCN parameters from RCNparameter.txt
    atom    = parameters_setup['atom']
    charge  = parameters_setup['charge']
    edge    = parameters_setup['edge']
    rcn_file = parameters_setup['rcn_file']

    rcn = parse_rcn_parameters(atom, charge, edge, rcn_file)

    # Template for the file
    template = f"""# Number of valence and final states to calculate
# These parameters are not used in Greens function calculation!
NPsi_Initial = {parameters_i['NPsi_i']}
NPsi_Final = {parameters_f['NPsi_f']}

# Initial state selection: 1 = ground state, higher numbers = excited states
initial_state = {parameters_setup['initial_state']}

# Ligand field parameters
tenDq_3d_i = {parameters_i['tenDq_3d_i']}
tenDq_3d_f = {parameters_f['tenDq_3d_f']}

Ds_3d_i = {parameters_i['Ds_3d_i']}
Ds_3d_f = {parameters_f['Ds_3d_f']}

Dt_3d_i = {parameters_i['Dt_3d_i']}
Dt_3d_f = {parameters_f['Dt_3d_f']}

# Scaling of Slater integrals
scalef2_3d3d_i = {parameters_i['scalef2_3d3d_i']}
scalef2_3d3d_f = {parameters_f['scalef2_3d3d_f']}

scalef4_3d3d_i = {parameters_i['scalef4_3d3d_i']}
scalef4_3d3d_f = {parameters_f['scalef4_3d3d_f']}

scalef2_2p3d = {parameters_f['scalef2_2p3d']}

scaleg = {parameters_f['scaleg']}

scale_3dSOC_i = {parameters_i['scale_3dSOC_i']}
scale_3dSOC_f = {parameters_f['scale_3dSOC_f']}

scale_2pSOC = {parameters_f['scale_2pSOC']}

# Monopole electron-electron interactions
U_3d_3d_i = {parameters_i['U_3d_3d_i']}
U_3d_3d_f = {parameters_f['U_3d_3d_f']}
U_2p_3d_f = {parameters_f['U_2p_3d_f']}

# Core-excited states shift
E_2p = {parameters_f['E_2p']}

# Atomic RCN parameters — auto-looked up from RCNparameter.txt, do not edit manually
# atom = {atom}, charge = {charge}, edge = {edge}
# Number of 3d electrons (initial state)
NE_3d = {rcn['NE_3d']}
# Initial state (2p6 3dN): {atom}{charge}
F2_3d3d_i_rcn = {rcn['F2_3d3d_i_rcn']}
F4_3d3d_i_rcn = {rcn['F4_3d3d_i_rcn']}
zeta_3d_i_rcn = {rcn['zeta_3d_i_rcn']}
# Final state (2p5 3d(N+1)): {atom}{charge}
F2_3d3d_f_rcn = {rcn['F2_3d3d_f_rcn']}
F4_3d3d_f_rcn = {rcn['F4_3d3d_f_rcn']}
F2_2p3d_rcn = {rcn['F2_2p3d_rcn']}
G1_2p3d_rcn = {rcn['G1_2p3d_rcn']}
G3_2p3d_rcn = {rcn['G3_2p3d_rcn']}
zeta_3d_f_rcn = {rcn['zeta_3d_f_rcn']}
zeta_2p_rcn = {rcn['zeta_2p_rcn']}




"""

    # Write to file
    with open(output_file, 'w') as f:
        f.write(template)

    return output_file


def generate_inp_quanty_CT(parameters_i, parameters_f, parameters_setup, output_path, fname):
    """
    Generate .inp_quanty file for a charge-transfer (CT) calculation including
    LMCT (occupied ligand L1) and MLCT (unoccupied ligand L2) parameters.

    Uses the same parameters_i / parameters_f / parameters_setup structure as
    generate_inp_quanty(), with the following additional keys:

    Parameters:
    -----------
    parameters_i : dict
        All keys from generate_inp_quanty() plus:
        - tenDq_L1_i    : Oh crystal field splitting of occupied ligand (LMCT)
        - Delta_3d_L1_i : charge-transfer energy for LMCT
        - Veg_3d_L1_i   : eg hopping for LMCT
        - Vt2g_3d_L1_i  : t2g hopping for LMCT
        - tenDq_L2_i    : Oh crystal field splitting of unoccupied ligand (MLCT)
        - Delta_3d_L2_i : charge-transfer energy for MLCT
        - Veg_3d_L2_i   : eg hopping for MLCT
        - Vt2g_3d_L2_i  : t2g hopping for MLCT

    parameters_f : dict
        All keys from generate_inp_quanty() plus:
        - tenDq_L1_f, Delta_3d_L1_f, Veg_3d_L1_f, Vt2g_3d_L1_f  (LMCT, final state)
        - tenDq_L2_f, Delta_3d_L2_f, Veg_3d_L2_f, Vt2g_3d_L2_f  (MLCT, final state)

    parameters_setup : dict
        Same as generate_inp_quanty(). See that function for full description.

    output_path : str or Path
        Directory or full file path for the output file.

    fname : str
        Filename for the output file.

    Returns:
    --------
    output_file : Path
        Full path to the generated file.
    """

    # Convert to Path object
    output_path = Path(output_path)

    if output_path.is_dir():
        output_file = output_path / fname
    else:
        output_file = output_path

    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Look up atomic RCN parameters from RCNparameter.txt
    atom     = parameters_setup['atom']
    charge   = parameters_setup['charge']
    edge     = parameters_setup['edge']
    rcn_file = parameters_setup['rcn_file']

    rcn = parse_rcn_parameters(atom, charge, edge, rcn_file)

    template = f"""# Number of valence and final states to calculate
# These parameters are not used in Greens function calculation!
NPsi_Initial = {parameters_i['NPsi_i']}
NPsi_Final = {parameters_f['NPsi_f']}

# Initial state selection: 1 = ground state, higher numbers = excited states
initial_state = {parameters_setup['initial_state']}

# Ligand field parameters
tenDq_3d_i = {parameters_i['tenDq_3d_i']}
tenDq_3d_f = {parameters_f['tenDq_3d_f']}

Ds_3d_i = {parameters_i['Ds_3d_i']}
Ds_3d_f = {parameters_f['Ds_3d_f']}

Dt_3d_i = {parameters_i['Dt_3d_i']}
Dt_3d_f = {parameters_f['Dt_3d_f']}

# Scaling of Slater integrals
scalef2_3d3d_i = {parameters_i['scalef2_3d3d_i']}
scalef2_3d3d_f = {parameters_f['scalef2_3d3d_f']}

scalef4_3d3d_i = {parameters_i['scalef4_3d3d_i']}
scalef4_3d3d_f = {parameters_f['scalef4_3d3d_f']}

scalef2_2p3d = {parameters_f['scalef2_2p3d']}

scaleg = {parameters_f['scaleg']}

scale_3dSOC_i = {parameters_i['scale_3dSOC_i']}
scale_3dSOC_f = {parameters_f['scale_3dSOC_f']}

scale_2pSOC = {parameters_f['scale_2pSOC']}

# Monopole electron-electron interactions
U_3d_3d_i = {parameters_i['U_3d_3d_i']}
U_3d_3d_f = {parameters_f['U_3d_3d_f']}
U_2p_3d_f = {parameters_f['U_2p_3d_f']}

# Core-excited states shift
E_2p = {parameters_f['E_2p']}

# Charge transfer parameters — LMCT (occupied ligand L1)
tenDq_L1_i = {parameters_i['tenDq_L1_i']}
tenDq_L1_f = {parameters_f['tenDq_L1_f']}

Delta_3d_L1_i = {parameters_i['Delta_3d_L1_i']}
Delta_3d_L1_f = {parameters_f['Delta_3d_L1_f']}

Veg_3d_L1_i = {parameters_i['Veg_3d_L1_i']}
Veg_3d_L1_f = {parameters_f['Veg_3d_L1_f']}

Vt2g_3d_L1_i = {parameters_i['Vt2g_3d_L1_i']}
Vt2g_3d_L1_f = {parameters_f['Vt2g_3d_L1_f']}

# Charge transfer parameters — MLCT (unoccupied ligand L2)
tenDq_L2_i = {parameters_i['tenDq_L2_i']}
tenDq_L2_f = {parameters_f['tenDq_L2_f']}

Delta_3d_L2_i = {parameters_i['Delta_3d_L2_i']}
Delta_3d_L2_f = {parameters_f['Delta_3d_L2_f']}

Veg_3d_L2_i = {parameters_i['Veg_3d_L2_i']}
Veg_3d_L2_f = {parameters_f['Veg_3d_L2_f']}

Vt2g_3d_L2_i = {parameters_i['Vt2g_3d_L2_i']}
Vt2g_3d_L2_f = {parameters_f['Vt2g_3d_L2_f']}

# Atomic RCN parameters — auto-looked up from RCNparameter.txt, do not edit manually
# atom = {atom}, charge = {charge}, edge = {edge}
# Number of 3d electrons (initial state)
NE_3d = {rcn['NE_3d']}
# Initial state (2p6 3dN): {atom}{charge}
F2_3d3d_i_rcn = {rcn['F2_3d3d_i_rcn']}
F4_3d3d_i_rcn = {rcn['F4_3d3d_i_rcn']}
zeta_3d_i_rcn = {rcn['zeta_3d_i_rcn']}
# Final state (2p5 3d(N+1)): {atom}{charge}
F2_3d3d_f_rcn = {rcn['F2_3d3d_f_rcn']}
F4_3d3d_f_rcn = {rcn['F4_3d3d_f_rcn']}
F2_2p3d_rcn = {rcn['F2_2p3d_rcn']}
G1_2p3d_rcn = {rcn['G1_2p3d_rcn']}
G3_2p3d_rcn = {rcn['G3_2p3d_rcn']}
zeta_3d_f_rcn = {rcn['zeta_3d_f_rcn']}
zeta_2p_rcn = {rcn['zeta_2p_rcn']}




"""

    with open(output_file, 'w') as f:
        f.write(template)

    return output_file

from pathlib import Path

def generate_inp_rixs(parameters_rixs, output_path, fname):
    """
    Generate .inp_rixs file with specified parameters.

    Parameters:
    -----------
    parameters_rixs : dict
        RIXS parameters. Expected keys:
        - energy_start
        - energy_end
        - energy_step
        - loss_start
        - loss_end
        - loss_step
        - FWHM_lorentz1
        - FWHM_lorentz1b
        - FWHM_lorentz2
        - Eshift
        - L3_L2_split
        - pol

        Note: initial_state has moved to parameters_setup in generate_inp_quanty.
    
    output_path : str or Path
        Path where the .inp_rixs file should be written
        (can be a directory or full file path)
    
    fname : str
        Filename for the output file
    
    Returns:
    --------
    output_file : Path
        Full path to the generated file
    """
    
    # Convert to Path object
    output_path = Path(output_path)
    
    # If output_path is a directory, append filename
    if output_path.is_dir():
        output_file = output_path / fname
    else:
        output_file = output_path
    
    # Create parent directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Template for the file
    template = f"""###
energy_start = {parameters_rixs['energy_start']}
energy_end = {parameters_rixs['energy_end']}
energy_step = {parameters_rixs['energy_step']}
#
loss_start = {parameters_rixs['loss_start']}
loss_end = {parameters_rixs['loss_end']}
loss_step = {parameters_rixs['loss_step']}

### Broadening parameters
# lifetime broadening at L3 edge
FWHM_lorentz1 = {parameters_rixs['FWHM_lorentz1']}
# lifetime broadening at L2 edge
FWHM_lorentz1b = {parameters_rixs['FWHM_lorentz1b']}
# lifetime broadening of the valence states
FWHM_lorentz2 = {parameters_rixs['FWHM_lorentz2']}

###
Eshift = {parameters_rixs['Eshift']}
L3_L2_split = {parameters_rixs['L3_L2_split']}

# This parameter are not used in Greens function calculation!
# pol is the angle between incident polarization plane and scattering plane
# 0 -> in pol-plane (horizontal)
# pi/2 -> 90 deg out of pol-plane (vertical)
# arccos(1/sqrt(3)) -> magic angle
pol = {parameters_rixs['pol']}




"""
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(template)
    
    return output_file
