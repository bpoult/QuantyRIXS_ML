import subprocess
import os
import shutil
from pathlib import Path

def run_quanty_sim(folder_path, lua_file="greenMLCT_Co3d6_D4h_RCN_conf_job.lua", lua_file_path=None, timeout=None):
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
        print(f"Copied {source_file} to {destination}")
    
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
        command = f"quanty {lua_file}"
        
        
        if lua_file != 'groundstate.lua':
            # Run simulation
            result = subprocess.run(
                command,
                shell=True,
                capture_output=False,
                text=True,
                timeout=timeout
            )
        else:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
        
        # Check if simulation succeeded
        if result.returncode != 0:
            print(f"Warning: Simulation returned non-zero exit code: {result.returncode}")
            print(f"STDERR: {result.stderr}")
        
        return result
        
    finally:
        # Always return to original directory
        os.chdir(original_dir)