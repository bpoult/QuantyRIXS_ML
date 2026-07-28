#!/bin/bash
#SBATCH --job-name=quanty_dataset
#SBATCH --account=lcls:default
#SBATCH --array=0-39                      # 10 batches (fill in based on num_batches)
#SBATCH --ntasks=1                       # 1 task per array job
#SBATCH --cpus-per-task=1              # 1 CPU per task
#SBATCH --mem=4G                         # memory per task
#SBATCH --time=00:45:00                # time limit per task 
#SBATCH --partition=milano
#SBATCH --output=logs/batch_%a.log    # one log file per batch
#SBATCH --error=logs/batch_%a.err      # one error file per batch

# ── Environment ───────────────────────────────────────────────
export PYTHONPATH=/sdf/home/p/pierop/QuantyRIXS_ML

# ── Run dataset generation for this batch ─────────────────────
python3 /sdf/home/p/pierop/QuantyRIXS_ML/scripts/generate_dataset.py \
    --N 20000 \
    --batch_index $SLURM_ARRAY_TASK_ID \
    --batch_size 500 \
    --complex co_terpy \
    --spectrum_type L3L2 \
    --output_path /sdf/home/p/pierop/QuantyRIXS_ML/data \
    --lua_file_path /sdf/home/p/pierop/QuantyRIXS_ML/