#!/bin/bash
#SBATCH --job-name=task_fit_reg_nPRF
#SBATCH --output=/home/mrenke/logs/regression_nPRF_stressrisk_%A-%a.txt
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --mem=96G
#SBATCH --time=12:00:00

source /etc/profile.d/lmod.sh
module load gpu cuda

# . $HOME/init_conda.sh

. $HOME/.bashrc

module load mamba
conda init
source activate numrefields

export PARTICIPANT_LABEL=$(printf "%02d" $SLURM_ARRAY_TASK_ID)

python $HOME/git/stress_risk/stress_risk/fmri_analysis/encoding_model/fit_regression_encoding_model.py $PARTICIPANT_LABEL --bids_folder /shares/zne.uzh/mrenke/ds-stressrisk 
