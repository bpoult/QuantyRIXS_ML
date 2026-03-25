import numpy as np
from itertools import product
from run_quanty_sim import run_quanty_sim

# Define parameter ranges
param_ranges = {
    'param1': (min1, max1),
    'param2': (min2, max2),
    # ... etc
}


num_parameters = param_ranges.shape()

# Use Latin Hypercube or random sampling
from scipy.stats import qmc
sampler = qmc.LatinHypercube(d=num_parameters)
samples = sampler.random(n=50000)

# Scale to your parameter ranges
scaled_samples = qmc.scale(samples, 
                           [ranges[0] for ranges in param_ranges.values()],
                           [ranges[1] for ranges in param_ranges.values()])

# Run simulations
spectra = []
parameters = []
for param_set in scaled_samples:
    spectrum = run_quanty_sim(param_set)
    spectra.append(spectrum)
    parameters.append(param_set)

# Save everything
np.save('spectra_data.npy', spectra)
np.save('parameters_data.npy', parameters)