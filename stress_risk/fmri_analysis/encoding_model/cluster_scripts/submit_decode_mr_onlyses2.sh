#!/bin/bash
#SBATCH --job-name=decode_volume
#SBATCH --output=/home/mrenke/logs/decode_volume_%A-%a.txt
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

python $HOME/git/stress_risk/stress_risk/fmri_analysis/encoding_model/decode.py $PARTICIPANT_LABEL 2 --bids_folder /scratch/mrenke/ds-stressrisk --n_voxels 250 --mask NPC_R  --denoise