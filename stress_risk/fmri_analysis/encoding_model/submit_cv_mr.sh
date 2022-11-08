#!/bin/bash
#SBATCH --job-name=task_fit_cv
#SBATCH --output=/home/cluster/mrenke/logs/fit_nprf_denoise_%A-%a.txt
#SBATCH --partition=volta
#SBATCH --ntasks=1
#SBATCH --mem=96G
#SBATCH --gres gpu:1
#SBATCH --time=2:00:00
module load volta
module load nvidia/cuda11.2-cudnn8.1.0

# . $HOME/init_conda.sh

. $HOME/.bashrc.sh

export PARTICIPANT_LABEL=$(printf "%02d" $SLURM_ARRAY_TASK_ID)

conda activate numrefields_02
python $HOME/git/stress_risk/stress_risk/fmri_analysis/encoding_model/fit_model_cv.py $PARTICIPANT_LABEL 1 --bids_folder /data/mrenke/ds-stressrisk --denoise

