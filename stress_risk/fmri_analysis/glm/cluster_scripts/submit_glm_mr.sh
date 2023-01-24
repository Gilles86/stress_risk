#!/bin/bash
#SBATCH --job-name=fit_st_denoise
#SBATCH --output=/home/mrenke/logs/fit_st_denoise_%A-%a.txt
#SBATCH --ntasks=1
#SBATCH -c 16
#SBATCH --time=45:00

. $HOME/.bashrc

source activate numrefields

export PARTICIPANT_LABEL=$(printf "%02d" $SLURM_ARRAY_TASK_ID)

python $HOME/git/stress_risk/stress_risk/fmri_analysis/glm/fit_glm_denoise.py $PARTICIPANT_LABEL 1 --bids_folder /scratch/mrenke/ds-stressrisk
python $HOME/git/stress_risk/stress_risk/fmri_analysis/glm/fit_glm_denoise.py $PARTICIPANT_LABEL 2 --bids_folder /scratch/mrenke/ds-stressrisk
