import numpy as np
from scipy.signal import correlate, correlation_lags
from scipy.interpolate import interp1d
from src.utils import setup_logger

logger = setup_logger()

def standardize_spectrum(energies: np.ndarray, intensities: np.ndarray, reference_grid: np.ndarray):
    '''
    Interpolates the Quanty energy array onto a reference grid with a defined energy axis and force every spectrum on it
    Normalizes the intensities so it relative to the highest intensity at 1.

    Parameters:
    -----------
    energies : np.ndarray, shape (1, n_energy_points) 
        Energy array produced by Quanty spectrum output
    intensities : np.ndarray, shape (1, n_energy_points) 
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


def interpolate_spectrum(original_grid: np.ndarray, intensities: np.ndarray, reference_grid: np.ndarray, kind='cubic'):
    """
    Interpolate a spectrum from one energy grid onto another (reference) grid.
    
    Example use case:
    - You have spectrum on reference_grid
    - You shift it (original_grid = reference_grid + energy_shift)
    - You want to resample it back onto reference_grid
    """
    original_grid = np.asarray(original_grid, dtype=float).flatten()
    intensities = np.asarray(intensities, dtype=float).flatten()
    reference_grid = np.asarray(reference_grid, dtype=float).flatten()
    
    # Sort if needed
    if np.any(np.diff(original_grid) < 0):
        order = np.argsort(original_grid)
        original_grid = original_grid[order]
        intensities = intensities[order]
    
    # Create interpolator from shifted spectrum
    interpolator = interp1d(original_grid, intensities, 
                           kind=kind, 
                           bounds_error=False,
                           fill_value=(intensities[0], intensities[-1]))
    
    # Resample back onto reference grid
    interp_spectrum = interpolator(reference_grid)
    
    return interp_spectrum.reshape(1, -1)

def align_spectrum(spectrum_to_shift: np.ndarray, target_spectrum: np.ndarray, reference_grid: np.ndarray):
    """
    Align one spectrum to a target spectrum via cross-correlation.

    Finds the optimal energy shift for spectrum_to_shift to match target_spectrum,
    then resamples the shifted spectrum back onto the reference grid.

    Parameters
    ----------
    spectrum_to_shift : np.ndarray, shape (n_energy_points,)
        The spectrum to be shifted. Currently the experimental spectrum;
        will be swapped to predicted spectrum once model is more generalized.
    target_spectrum : np.ndarray, shape (n_energy_points,)
        The fixed reference spectrum to align against. Currently the mean
        training spectrum; will be swapped to experimental later.
    reference_grid : np.ndarray, shape (n_energy_points,)
        Energy grid (eV) that all spectra are standardized to.
        Must be evenly-spaced.

    Returns
    -------
    spectrum_interp : np.ndarray, shape (1, n_energy_points)
        Shifted spectrum resampled onto reference_grid.
    energy_shift : float
        Energy shift (eV) applied. Positive = shifted to higher energy.
    """
    # Flatten both spectra to 1D for cross-correlation
    spec_to_shift = spectrum_to_shift.flatten()
    target_spec = target_spectrum.flatten()

    # Compute cross-correlation — finds how much spec_to_shift needs to move to match target_spec
    correlation = correlate(spec_to_shift, target_spec, mode='same')

    # Get the lag values in index units
    lags = correlation_lags(len(spec_to_shift), len(target_spec), mode='same')

    # Find the lag index where correlation is maximized — this is the optimal shift
    offset_index = lags[np.argmax(correlation)]

    # Convert index offset to energy units (eV)
    x_spacing = reference_grid[1] - reference_grid[0]
    energy_shift = -offset_index * x_spacing

    logger.info(f"Energy shift for alignment: {energy_shift:.4f} eV")

    # Shift the energy grid by energy_shift and resample spectrum back onto original reference grid
    shifted_grid = reference_grid + energy_shift
    spectrum_interp = interpolate_spectrum(original_grid=shifted_grid, intensities=spec_to_shift, reference_grid=reference_grid)

    return spectrum_interp, energy_shift