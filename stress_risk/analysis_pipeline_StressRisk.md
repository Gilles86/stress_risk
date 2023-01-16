#  analysis pipeline StressRisk

## 1. data preparation and preprocessing
### 1.1. Copy data

* behavioral: `/Volumes/g_department$/projects/2022/renkert_dehollander_aydogan_ruff_stress_risk_fMRI/data/logs`
[on stimulus computer: `C:\expFiles\Maie\stress_risk\experiments\logs`]

* MRI: `/Volumes/g_econ_rawdata$/rawdata/2022/*mont*/*day*/SNS_MRI_MRISK_S......`

* on sciencecloud `for day in 11 16 17 18; do cp -rv /econ_rawdata/rawdata/2022/11/${day}/SNS_MRI_MRISK_S* /data/ds-stressrisk/sourcedata/mri/; done;`
--> into ~/data/ds-stressrisk/sourcedata\




### 1.2. put into correct data format:

* (`conda activate numrefields`)
* `cd /Users/mrenke/git/stress_risk/stress_risk/prepare`
* `for subject in 16; do python convert_raw_mri_data.py $subject 1 --bids_folder /Users/mrenke/data/ds-stressrisk ; done;`
* `for subject in 28 29 30 31 32 33 34 35 36 37 38 39 40; do python convert_behavior.py $subject 1 --bids_folder /Users/mrenke/data/ds-stressrisk ; done;`
01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60
01 02 03 04 05 07 09 10 12 13 14 16 17 18 19 21 22 23 24 25 26 28 30 31 32 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 57 58 59

### 1.3. Frmiprep 
#### 1.3.1. on sciencecloud

* put data on sciencecloud: `rsync -r  ~/data/ds-stressrisk/sub-03 sciencecloud:/data/ds-stressrisk/` or `for subject in 04 05 06 07; do rsync -r  ~/data/ds-stressrisk/sub-$subject sciencecloud:/data/ds-stressrisk/ ; done;`
* `tmux attach-session -t 0` [other tmux commands: `tmux ls`; start new session`tmux` ; end all session: `tmux kill-server`, ]
* `fmriprep-docker --fs-license-file $HOME/freesurfer/license.txt /data/ds-stressrisk /data/ds-stressrisk/derivatives/ --output-spaces MNI152NLin2009cAsym T1w fsaverage fsnative  --dummy-scans 3 --skip_bids_validation --participant_label 31 33 34 35 36 37 38 39 40 --work-dir /data/tmp` #carefull the -- does not become
    * check fmriprep created temporary files (/tmp/workflow...) that can take up a lot of space on the VM. /data should be mounted to the attached Volume (1 TB)
* put preprcoessed data back on my computer: `rsync -r  sciencecloud:/data/ds-stressrisk/derivatives ~/data/ds-stressrisk/derivatives`
* `for subject in 31 33 34 35 36 37 38 39 40; do fmriprep-docker --fs-license-file $HOME/freesurfer/license.txt /data/ds-stressrisk /data/ds-stressrisk/derivatives/ --output-spaces MNI152NLin2009cAsym T1w fsaverage fsnative  --dummy-scans 3 --skip_bids_validation --participant_label $subject --work-dir /data/tmp; done;`

#### 1.3.2. on sciencecluster

* for subject in 01 02 03 04 05 07 09 10 12 13 14 16 17 18 19 21 22 23 24 25 26 28 30 31 32 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 57 58 59; do rsync -rcvz sciencecloud:/data/ds-stressrisk/sub-${subject} /data/mrenke/ds-stressrisk ; done; 
* `rsync -rcvz ....`
`cd /home/cluster/mrenke/git/stress_risk/stress_risk/cluster_preprocess/`
`sbatch --array=03,04 fmriprep.sh`
`squeue -u mrenke`
`squeue -u mrenke --array -j --format="%.25i %.9P %.30j %.10u %.2t %.10M %.6D %R"`
* logs can be found in `~/logs` & `ls` 
* then `rsync -r sciencecluster:/data/mrenke/ds-stressrisk/derivatives/fmriprep/sub-19 ~/data/ds-stressrisk/derivatives/fmriprep` (correct folder format!!)
* rsync -rcvz data/ds-stressrisk/sub-{18,19}

### 1.4. retrcoir confounds
* open `Matlab`, go to folder `/Users/mrenke/git/stress_risk/stress_risk/physiology`
* takes: `~/data/ds-stressrisk/sub-{}}/ses-{}/func/sub-{}_ses-{}_task-risk_run-{}_physio.log`
* writes to: `bids_folder/derivatives/physiotoolbox/sub-{}` 

## 2. fMRI-analysis pipeline
* (`conda activate numrefields`)
* `cd /Users/mrenke/git/stress_risk/stress_risk/fmri_analysis`

### 2.1. get activations: fit betas to single trials
* `python fit_single_trials.py 03 1` [= subject session; '--bids_folder', default='/data/ds-stressrisk', '--smoothed', action='store_true', --pca_confounds', action='store_true'] 

### 2.2. encoder: fit nprfs
* `python fit_nprf.py 03 1` [= subject session; '--bids_folder', default='/data/ds-stressrisk', '--smoothed', action='store_true', --pca_confounds', action='store_true'] 

### 2.3. construct sub specific IPS-masks
* `cd /Users/mrenke/git/stress_risk/stress_risk/fmri_analysis/surface`
* 1. `python transform_npc.py 01` [--hemi R = default]
* 2. `python npc_to_volume.py 01`

### 2.4. decoder: crossVal-encoder and then decoder
* `cd /Users/mrenke/git/stress_risk/stress_risk/fmri_analysis`
* `fit_task_crossVal.py`
* `decoder.py`

### 

## Visualize and R2-based subject filtering


## Analysis on sciencecluster

* set up environment: `conda env create -n numrefields_sc --file ENV.yml`
* log into GPU node: `srun --time=2:00:00 --partition=volta --gres gpu:1 --pty /bin/bash -i `
* activate env: `conda activate numrefields_02` [which works]
* load CUDA drivers (for GPU computing): `module load volta nvidia/cuda11.2-cudnn8.1.0`
* then run loop:  `for subject in 23 24 25 26 27; do python fit_nprf.py $subject 1 
smoothed; done;`
python fit_task_crossVal.py 21 1 --bids_folder /data/mrenke/ds-stressrisk
sbatch --array=16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 cluster_fit_cv.sh

`for subject in 30 31 32 33 34 35 36 37 38 39 40; do python fit_single_trials.py $subject 1 --bids_folder /data/mrenke/ds-stressrisk --smoothed; done;`

# SubList

* for preprocessing on sciencecluster: `01,05,12,17,22,26,32,37,41,45,49,53,58,02,07,13,18,23,28,34,38,42,46,50,54,59,03,09,14,19,24,30,35,39,43,47,51,55,04,10,16,21,25,31,36,40,44,48,52,57`

* from `...stress_risk/prepare/get_subList-String.py`:
* * on local: `13 14 22 25 49 40 47 24 23 15 12 46 41 48 13 10 15 16 16 14 52 55 30 08 37 01 39 06 54 53 38 07 09 36 31 44 43 17 28 10 26 19 21 42 45 20 27 18 11 16 29 13 15 11 34 33 05 02 56 51 58 03 04 32 35 59 50 57` 

* * on sciencecloud: `12 17 18 61 22 21 34 40 33 14 09 57 41 03 50 04 44 13 51 26 59 48 19 52 11 46 56 10 23 39 31 25 08 42 05 53 20 28 47 54 45 35 29 07 36 16 01 32 58 37 43 49 55 27 38 15 24 30 06 02 `