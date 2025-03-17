#!/bin/bash
#SBATCH --job-name=fit_st_denoise
#SBATCH --output=/home/mrenke/logs/stress_risk_logs/fit_st_denoise_bothSes_%A-%a.txt
#SBATCH --ntasks=1
#SBATCH -c 16
#SBATCH --mem=16G 
#SBATCH --time=3:00:00

. $HOME/.bashrc

source activate numrefields

export PARTICIPANT_LABEL=$(printf "%02d" $SLURM_ARRAY_TASK_ID)

python $HOME/git/stress_risk/stress_risk/fmri_analysis/glm/fit_glm_denoise.py $PARTICIPANT_LABEL 1 --bids_folder /shares/zne.uzh/mrenke/ds-stressrisk --smoothed
python $HOME/git/stress_risk/stress_risk/fmri_analysis/glm/fit_glm_denoise.py $PARTICIPANT_LABEL 2 --bids_folder /shares/zne.uzh/mrenke/ds-stressrisk --smoothed
