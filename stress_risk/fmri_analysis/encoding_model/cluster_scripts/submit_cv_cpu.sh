#!/bin/bash
#SBATCH --job-name=task_fit_cv_cpu
#SBATCH --output=/home/cluster/gdehol/logs/fit_nprf_smoothed_surf_%A-%a.txt
#SBATCH --partition=generic
#SBATCH --ntasks=1
#SBATCH -c32
#SBATCH --mem=96G
#SBATCH --time=2:00:00

# . $HOME/init_conda.sh
# . $HOME/init_freesurfer.sh
. $HOME/.bashrc.sh

export PARTICIPANT_LABEL=$(printf "%02d" $SLURM_ARRAY_TASK_ID)

source activate tf2-gpu
python $HOME/git/stress_risk/stress_risk/fmri_analysis/encoding_model/fit_model_cv.py $PARTICIPANT_LABEL 1 --bids_folder /scratch/gdehol/ds-stressrisk --denoise
python $HOME/git/stress_risk/stress_risk/fmri_analysis/encoding_model/fit_model_cv.py $PARTICIPANT_LABEL 1 --bids_folder /scratch/gdehol/ds-stressrisk --smoothed --denoise
