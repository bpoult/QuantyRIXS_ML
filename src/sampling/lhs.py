from scipy.stats import qmc
import numpy as np

def latin_hypercube_sampling(N: int, d: int, l_bounds: list, u_bounds: list) -> np.ndarray:
    """
    Generate N samples across d parameters using Latin Hypercube Sampling.
    Guarantees even coverage of the parameter space by placing exactly one
    sample per stratum across each dimension.

    Parameters:
    -----------
    N : int
        Number of samples to generate.
    d : int
        Number of dimensions (parameters) to sample.
    l_bounds : list
        Lower bounds for each parameter, length d.
    u_bounds : list
        Upper bounds for each parameter, length d.
    seed : int
        Random seed for reproducibility. Default 1.

    Returns:
    --------
    scaled : np.ndarray, shape (N, d)
        Sampled parameter values scaled to [l_bounds, u_bounds].
    """

    # Initialize the LHS sampler for d dimensions with a fixed seed for reproducibility
    sampler = qmc.LatinHypercube(d=d, seed=1)

    # Generate N samples in the unit hypercube [0, 1]^d — one sample per stratum per dimension
    sample = sampler.random(n=N)

    # Scale samples from [0, 1] to the actual parameter ranges
    scaled = qmc.scale(sample, l_bounds, u_bounds)

    return scaled