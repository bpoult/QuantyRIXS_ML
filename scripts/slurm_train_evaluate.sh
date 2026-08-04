#!/bin/bash
#SBATCH --job-name=quanty_train
#SBATCH --account=lcls:default
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --partition=milano
#SBATCH --constraint=OS_VER:8.6
#SBATCH --output=logs/train_eval.log
#SBATCH --error=logs/train_eval.err

export PYTHONPATH=/sdf/home/p/pierop/QuantyRIXS_ML

/sdf/group/lcls/ds/ana/sw/conda1/inst/envs/ana-4.0.68-py3/bin/python3 \
    /sdf/home/p/pierop/QuantyRIXS_ML/scripts/evaluate_model.py \
    --complex co_terpy \
    --spectrum_type L3L2 \
    --initial_state 1 \
    --mode CF
    --lua_file_path /sdf/home/p/pierop/QuantyRIXS_ML/