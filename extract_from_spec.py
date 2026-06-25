import subprocess
import os
import shutil
import numpy as np
from pathlib import Path


def extract_from_spec(folder_path, spec_file, timeout=None):
    """
    Take the Quanty XAS output data then extract the Energy and Intensity Column

    Parameters:
    -----------
    folder_path : str or Path
        Path to folder containing .txt file
    spec_file : str
        Name of the Quanty Output file to parse
    timeout : int, optional
        Maximum time in seconds to wait for simulation (default: None, no timeout)
    
    Returns:
    --------
    result : subprocess.CompletedProcess
        Contains return code, stdout, stderr
    
    Raises:
    -------
    FileNotFoundError : if folder or output file doesn't exist
    subprocess.TimeoutExpired : if simulation exceeds timeout
    """

    #Convert to Path object for easier manipulation
    folder_path = Path(folder_path)

    # Verify folder exists
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    spec_path = folder_path / spec_file

    if not spec_path.exists():
        raise FileNotFoundError(f"File not found: {spec_path}")
    
    data = np.loadtxt(spec_path)

    
