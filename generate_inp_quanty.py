from pathlib import Path
from parse_rcn import parse_rcn_parameters


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