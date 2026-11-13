#!/bin/bash
#SBATCH --job-name=nprf_fit_joint_alphagaussian_cv
#SBATCH --ntasks=1
#SBATCH --time=120:00
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G  # Request more memory
#SBATCH --gres gpu:1

. $HOME/init_conda.sh
# . $HOME/init_freesurfer.sh
# . $HOME/.bashrc.sh

export PARTICIPANT_LABEL=$(printf "%02d" $SLURM_ARRAY_TASK_ID)

source activate tf2-gpu
# python $HOME/git/stress_risk/stress_risk/fmri_analysis/encoding_model/fit_model_cv.py $PARTICIPANT_LABEL 1 --bids_folder /scratch/gdehol/ds-stressrisk --denoise
python $HOME/git/stress_risk/stress_risk/fmri_analysis/encoding_model/fit_model_cv.py $PARTICIPANT_LABEL 1 --bids_folder /scratch/gdehol/ds-stressrisk --smoothed --denoise --retroicor
python $HOME/git/stress_risk/stress_risk/fmri_analysis/encoding_model/fit_model_cv.py $PARTICIPANT_LABEL 2 --bids_folder /scratch/gdehol/ds-stressrisk --smoothed --denoise --retroicor
