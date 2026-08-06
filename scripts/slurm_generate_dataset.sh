#!/bin/bash
#SBATCH --job-name=quanty_dataset
#SBATCH --account=lcls:default
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:45:00
#SBATCH --partition=milano
#SBATCH --constraint=OS_VER:8.6
#SBATCH --output=logs/batch_%a.log
#SBATCH --error=logs/batch_%a.err

# ── Environment ───────────────────────────────────────────────
export PYTHONPATH=/sdf/home/p/pierop/QuantyRIXS_ML

# ── Run dataset generation for this batch ─────────────────────
/sdf/group/lcls/ds/ana/sw/conda1/inst/envs/ana-4.0.68-py3/bin/python3 /sdf/home/p/pierop/QuantyRIXS_ML/scripts/generate_dataset.py \
    --N 200000 \
    --batch_index $((SLURM_ARRAY_TASK_ID + OFFSET)) \
    --batch_size 500 \
    --complex co_terpy \
    --spectrum_type L3L2 \
    --initial_state 1\
    --mode CF
    --output_path /sdf/home/p/pierop/QuantyRIXS_ML/data \
    --lua_file_path /sdf/home/p/pierop/QuantyRIXS_ML/