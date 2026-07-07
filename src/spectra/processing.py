import numpy as np

def standardize_spectrum(energies: np.ndarray, intensities: np.ndarray, reference_grid: np.ndarray):
    '''
    Interpolates the Quanty energy array onto a reference grid with a defined energy axis and force every spectrum on it
    Normalizes the intensities so it relative to the highest intensity at 1.

    Parameters:
    -----------
    energies : np.ndarray
        Energy array produced by Quanty spectrum output
    intensities : np.ndarray
        Intensity array produced by Quanty spectrum output
    reference_grid : np.ndarray
        A fixed array of energy values that every spectrum gets resampled onto
    
    Returns:
    --------
    standardized_spectrum : np.ndarray
        An interpolated and normalized spectrum that lies within the reference_grid energy axis and a standard convention for
        the intensity axis

    '''
    normalized_intensities = intensities / np.max(intensities)
    standardized_spectrum = np.interp(reference_grid, energies, normalized_intensities)

    return standardized_spectrum