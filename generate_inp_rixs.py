from pathlib import Path

def generate_inp_rixs(parameters_rixs, output_path, fname):
    """
    Generate .inp_rixs file with specified parameters.
    
    Parameters:
    -----------
    parameters_rixs : dict
        RIXS parameters. Expected keys:
        - initial_state
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
    template = f"""# initial state, 1 = ground state
initial_state = {parameters_rixs['initial_state']}

###
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