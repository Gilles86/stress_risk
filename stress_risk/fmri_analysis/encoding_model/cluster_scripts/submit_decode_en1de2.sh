#!/bin/bash
#SBATCH --job-name=decode_volume
#SBATCH --output=/home/mrenke/logs/stress_risk_logs/decode_svox_en1-de2_%A-%a.txt
#SBATCH --ntasks=1
#SBATCH --mem=96G
#SBATCH --gpus=V100:1 --constraint=GPUMEM32GB
#SBATCH --time=3:00:00

source /etc/profile.d/lmod.sh
module load gpu cuda

# . $HOME/init_conda.sh

. $HOME/.bashrc.sh

source activate numrefields

export PARTICIPANT_LABEL=$(printf "%02d" $SLURM_ARRAY_TASK_ID)

source activate tf2-gpu

python $HOME/git/stress_risk/stress_risk/fmri_analysis/encoding_model/decode_svoxels.py $PARTICIPANT_LABEL --bids_folder /shares/zne.uzh/mrenke/ds-stressrisk --mask NPC1_R  --denoise --retroicor
python $HOME/git/stress_risk/stress_risk/fmri_analysis/encoding_model/decode_svoxels.py $PARTICIPANT_LABEL --bids_folder /shares/zne.uzh/mrenke/ds-stressrisk --mask NPC3_R  --denoise --retroicor