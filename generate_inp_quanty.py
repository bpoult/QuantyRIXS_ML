from pathlib import Path

def generate_inp_quanty(parameters_i, parameters_f, output_path,fname):
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
    
    
    output_path : str or Path
        Path where the .inp_quanty file should be written
        (can be a directory or full file path)
    
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
    template = f"""# Number of valence and final states to calculate
# These parameters are not used in Greens function calculation!
NPsi_Initial = {parameters_i['NPsi_i']}
NPsi_Final = {parameters_f['NPsi_f']}

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




"""
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(template)
    
    return output_file