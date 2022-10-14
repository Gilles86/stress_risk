#!/bin/bash
#SBATCH --job-name=fit_st_denoise
#SBATCH --output=/home/cluster/gdehol/logs/fit_st_denoise_%A-%a.txt
#SBATCH --partition=generic
#SBATCH --ntasks=1
#SBATCH -c 16
#SBATCH --time=45:00

. $HOME/.bashrc

export PARTICIPANT_LABEL=$(printf "%02d" $SLURM_ARRAY_TASK_ID)

python $HOME/git/stress_risk/stress_risk/fmri_analysis/glm/fit_glm_denoise.py $PARTICIPANT_LABEL 1 --bids_folder /scratch/gdehol/ds-stressrisk --smoothed
python $HOME/git/stress_risk/stress_risk/fmri_analysis/glm/fit_glm_denoise.py $PARTICIPANT_LABEL 1 --bids_folder /scratch/gdehol/ds-stressrisk
