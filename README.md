This project utilizes Quanty for simulating transition metal X-ray spectroscopy which can be found here:

https://www.quanty.org/start

Efficient real-frequency solver for dynamical mean-field theory
Y. Lu, M. Hoeppner, O. Gunnarsson, and M.W. Haverkort
Phys. Rev. B 90, 085102 (2014).

Bands, resonances, edge singularities and excitons in core level spectroscopy investigated within the dynamical mean-field theory
M.W. Haverkort, G. Sangiovanni, P. Hansmann, A. Toschi, Y. Lu, and S. Macke
Euro. Phys. Lett. 108, 57004 (2014).

Multiplet ligand-field theory using Wannier orbitals
M.W. Haverkort, M. Zwierzcki, and O.K. Andersen
Phys. Rev. B 85, 165113 (2012).

# QuantyRIXS_ML

Machine learning pipeline for predicting crystal field and charge transfer parameters from X-ray absorption spectra (XAS) of transition metal complexes. Uses gradient boosting (LightGBM) trained on Quanty CTM simulations.

---

## Overview

The pipeline has two workflows depending on where you are working:

- **S3DF (SLAC HPC)** — dataset generation, model training, and evaluation. All compute-heavy work runs here via Slurm array jobs.
- **Local machine** — experimental spectrum fitting, plotting, and analysis. Clone the repo and use the included pre-trained models to get started immediately without training.

---

## Repository Structure

```
QuantyRIXS_ML/
├── configs/                    # Per-complex config files and parameter bounds
│   ├── co_terpy_L3L2_state1_CF_params.json
│   ├── param_bounds.json       # LHS sampling bounds for CF and CT
│   └── ...
├── data/
│   ├── experimental/           # Experimental spectra (.txt files)
│   └── {complex}_{type}_state{n}_{mode}_data/   # Generated datasets
├── models/                     # Trained model files (.joblib)
├── scripts/                    # Runnable entry points
│   ├── generate_dataset.py
│   ├── merge_datasets.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   ├── fit_experiment.py
│   ├── slurm_generate_dataset.sh
│   └── slurm_generate_dataset.sh 
├── src/                        # Reusable library code
│   ├── data/                   # HDF5 storage layer
│   ├── models/                 # ML model (train + evaluate)
│   ├── params/                 # CrystalFieldParams schema
│   ├── sampling/               # Latin Hypercube Sampling
│   ├── spectra/                # Quanty I/O and spectrum processing
│   └── utils/                  # Config loading, logging
├── logs/                       # Slurm and training logs
├── RCNparameter.txt            # Atomic RCN parameters for Quanty
└── requirements.txt
```

---

## Naming Convention

All datasets, models, and configs follow this pattern:

```
{complex}_{spectrum_type}_state{initial_state}_{mode}
```

Examples:
- `co_terpy_L3L2_state1_CF` — Co(terpy)2³⁺, L3+L2 edges, ground state, crystal field only
- `co_terpy_L3_state1_CT`  — Co(terpy)2³⁺, L3 only, ground state, charge transfer

---

## Local Setup (Fitting Only)

Use this workflow to fit experimental spectra using a pre-trained model. Pre-trained models and reference spectra are included directly in the repository — no separate download or training required.

### 1. Clone the repository

```bash
git clone https://github.com/bpoult/QuantyRIXS_ML.git
cd QuantyRIXS_ML
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Requires Python 3.9+ and Quanty installed at `~/bin/Quanty` (or on PATH as `Quanty`).

### 3. Pre-trained models

Pre-trained models are included in the `models/` folder of the repository and are ready to use immediately after cloning. No download needed.

If you trained a new model on S3DF and want to use it locally, copy it into `models/`:

```bash
scp <s3df_username>@s3dflogin.sdf.slac.stanford.edu:/path/to/QuantyRIXS_ML/models/<model_name>.joblib models/
```

Similarly, if you generated a new reference spectrum on S3DF, copy it into `data/`:

```bash
scp <s3df_username>@s3dflogin.sdf.slac.stanford.edu:/path/to/QuantyRIXS_ML/data/<complex_data_dir>/<reference_spectrum>.npy data/
```

### 4. Add your experimental spectrum

Place your experimental spectrum `.txt` file (two columns: energy, intensity, no header) in:

```
data/experimental/your_spectrum.txt
```

### 5. Run fit_experiment

```bash
export PYTHONPATH=/path/to/QuantyRIXS_ML
python3 scripts/fit_experiment.py \
    --experiment_file your_spectrum.txt \
    --complex co_terpy \
    --spectrum_type L3L2 \
    --initial_state 1 \
    --mode CF \
    --lua_file_path /path/to/QuantyRIXS_ML/
```

This will:
- Load the trained model
- Align the experimental spectrum to the training distribution
- Predict crystal field parameters
- Re-simulate with predicted parameters using Quanty
- Report RMSE, cosine similarity, and predicted parameters

---

## S3DF Workflow (Training)

Use this workflow to generate datasets, train models, and evaluate on S3DF.

### 1. SSH into S3DF and clone the repo

```bash
ssh user@s3dflogin.sdf.slac.stanford.edu
cd ~
git clone https://github.com/bpoult/QuantyRIXS_ML.git
cd QuantyRIXS_ML
```

### 2. Set up environment

```bash
export PYTHONPATH=$HOME/QuantyRIXS_ML
```

Add to `~/.bashrc` to make permanent:

```bash
echo 'export PYTHONPATH=$HOME/QuantyRIXS_ML' >> ~/.bashrc
source ~/.bashrc
```

### 3. Install Quanty

Upload the Linux Quanty binary via S3DF OnDemand file browser, then:

```bash
mkdir -p ~/.local/bin
mv ~/Quanty ~/.local/bin/Quanty
chmod +x ~/.local/bin/Quanty
```

### 4. Install dependencies

```bash
python3 -m pip install -r requirements.txt --user
```

### 5. Generate dataset (Slurm array job)

For 100k simulations across 200 batches of 500 each (max 100 per Slurm array):

```bash
mkdir -p logs
sbatch --array=0-99   --export=OFFSET=0   scripts/slurm_generate_dataset.sh
sbatch --array=0-99   --export=OFFSET=100 scripts/slurm_generate_dataset.sh
```

Monitor jobs:

```bash
squeue -u $USER
```

Check logs:

```bash
tail -f logs/batch_0.err
```

### 6. Merge batches after all jobs finish

```bash
python3 scripts/merge_datasets.py \
    --num_batches 200 \
    --complex co_terpy \
    --spectrum_type L3L2 \
    --initial_state 1 \
    --mode CF
```

This also generates the reference spectrum used for alignment.

### 7. Train model

```bash
nohup python3 scripts/train_model.py \
    --complex co_terpy \
    --spectrum_type L3L2 \
    --initial_state 1 \
    --mode CF > train.log 2>&1 &
```

### 8. Evaluate model

```bash
nohup python3 scripts/evaluate_model.py \
    --complex co_terpy \
    --spectrum_type L3L2 \
    --initial_state 1 \
    --mode CF \
    --lua_file_path $HOME/QuantyRIXS_ML/ > eval.log 2>&1 &
```

---

## Adding a New Complex

To extend the pipeline to a new complex (e.g. NiO, Fe(CN)6³⁻):

### 1. Create a config file

Copy an existing config and update the parameters:

```bash
cp configs/co_terpy_L3L2_state1_CF_params.json configs/nio_L3L2_state1_CF_params.json
```

Update `atom`, `charge`, `E_2p`, and broadening values in the new config. To find the correct `E_2p`:
- Run a test simulation with literature parameter values
- Compare to an experimental spectrum using cross-correlation
- Adjust `E_2p` until the energy shift is < 0.1 eV

### 2. Update parameter bounds

Add element-specific bounds to `configs/param_bounds.json` if needed.

### 3. Generate dataset

```bash
sbatch --array=0-99 --export=OFFSET=0 scripts/slurm_generate_dataset.sh
# Add --complex nio --spectrum_type L3L2 --initial_state 1 to the script
```

### 4. Train and evaluate

Same commands as above with `--complex nio`.

---

## Key Parameters

| Argument | Description | Example |
|---|---|---|
| `--complex` | Complex name | `co_terpy` |
| `--spectrum_type` | Edge coverage | `L3` or `L3L2` |
| `--initial_state` | Initial state number | `1` (ground state) |
| `--mode` | Simulation type | `CF` or `CT` |
| `--N` | Total simulations | `100000` |
| `--batch_size` | Simulations per Slurm task | `500` |

---

## Known Limitations

- **Parameter degeneracy**: Multiple parameter combinations can produce nearly identical spectra. The model finds a valid spectral match but may not recover the unique physical parameter set. Adding CT parameters is expected to reduce degeneracy.
- **CT simulation speed**: Charge transfer simulations take ~5 minutes each vs ~1.5 seconds for crystal field. CT dataset generation requires significant HPC time.
- **Energy calibration**: `E_2p` must be calibrated per-complex using cross-correlation against an experimental spectrum before generating training data.