#!/bin/bash
#SBATCH --job-name=decode_volume
#SBATCH --output=/home/mrenke/logs/decode_sel_vox_%A-%a.txt
#SBATCH --ntasks=1
#SBATCH --mem=96G
#SBATCH --gres gpu:1
#SBATCH --time=3:00:00

source /etc/profile.d/lmod.sh
module load gpu cuda

# . $HOME/init_conda.sh

. $HOME/.bashrc.sh

source activate numrefields

export PARTICIPANT_LABEL=$(printf "%02d" $SLURM_ARRAY_TASK_ID)

source activate tf2-gpu

python $HOME/git/stress_risk/stress_risk/fmri_analysis/encoding_model/decode_select_voxels_cv.py $PARTICIPANT_LABEL 1 --bids_folder /shares/zne.uzh/mrenke/ds-stressrisk --mask NPC_R  --denoise --retroicor
python $HOME/git/stress_risk/stress_risk/fmri_analysis/encoding_model/decode_select_voxels_cv.py $PARTICIPANT_LABEL 2 --bids_folder /shares/zne.uzh/mrenke/ds-stressrisk --mask NPC_R  --denoise --retroicor