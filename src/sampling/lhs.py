from scipy.stats import qmc
import numpy as np

def latin_hypercube_sampling(N: int, d: int, l_bounds: np.ndarray, u_bounds: np.ndarray):
    sampler = qmc.LatinHypercube(d=d, seed=1)

    sample = sampler.random(n=N)

    scaled = qmc.scale(sample, l_bounds, u_bounds)

    return scaled