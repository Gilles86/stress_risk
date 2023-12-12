#!/bin/bash
#SBATCH --job-name=mriqc
#SBATCH --output=/home/mrenke/logs/res_mriqc_group.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00
module load singularityce/3.10.2
export SINGULARITYENV_FS_LICENSE=$HOME/freesurfer/license.txt
export SINGULARITYENV_TEMPLATEFLOW_HOME=/opt/templateflow
export SINGULARITY_CACHEDIR=/data/mrenke/singularity

singularity run -u -B /shares/zne.uzh/$USER/ds-stressrisk:/data -B /scratch/$USER/workflow_folders:/workflow -B /scratch/$USER/templateflow:/opt/templateflow --cleanenv /data/$USER/mriqc-23.1.0.simg  /data /data/derivatives/mriqc group -m T1w bold
