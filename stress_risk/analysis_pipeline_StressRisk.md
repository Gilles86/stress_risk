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
* denoise (GLMsingle) variant: 

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


## Analysis on sciencecluster2

* set up environment: `conda env create -n numrefields_sc --file ENV.yml`
* log into GPU node: 
 `srun --pty -n 1 -c 2 --time=01:00:00 --gres=gpu:1 --mem=8G bash -l`
* activate env: `conda activate numrefields` [which works]
* load CUDA drivers (for GPU computing): `module load volta nvidia/cuda11.2-cudnn8.1.0`
* then run loop:  `for subject in 23 24 25 26 27; do python fit_nprf.py $subject 1 
smoothed; done;`
python fit_task_crossVal.py 21 1 --bids_folder /data/mrenke/ds-stressrisk
sbatch --array=16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 cluster_fit_cv.sh

`for subject in 30 31 32 33 34 35 36 37 38 39 40; do python fit_single_trials.py $subject 1 --bids_folder /data/mrenke/ds-stressrisk --smoothed; done;`
## Analysis on NEW sciencecluster
* first request interactive session to install anything!: `srun --pty -n 1 -c 2 --time=01:00:00 --gres=gpu:1 --mem=8G bash -l`
* 
for sub in 61
do
rsync -rzcv  --include="*/" --include="*.tsv" --include="*/ses-2/*" --exclude="*" ~/data/ds-stressrisk/sub-${sub}  sciencecluster2:/scratch/mrenke/ds-stressrisk

# SubList
* from `...stress_risk/prepare/get_subList-String.py` (only files for final data analysis):
* * `01 02 03 04 05 09 10 12 13 14 16 17 18 19 21 22 23 24 25 26 28 30 31 32 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 57 58 59 61`
* * `01,02,03,04,05,09,10,12,13,14,16,17,18,19,21,22,23,24,25,26,28,30,31,32,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,57,58,59,61`

## file placing for GLM on sciencecloud2

* copy physio files
ses=1
for sub in 01 02 03 05; do rsync -avz --include='*/' --include='*physio.log' --exclude='*' sciencecloud:/data/ds-stressrisk/sub-${sub}/ses-${ses}/func/ /Volumes/mrenkeED/data/ds-stressrisk/sub-${sub}/ses-${ses}/func ; done;
for sub in 01 02 03 05; do rsync /Volumes/mrenkeED/data/ds-stressrisk/sub-${sub}/ses-${ses}/func/*physio.log sciencecloud2:/mnt/ds-stressrisk/sub-${sub}/ses-${ses}/func ; done;
(repeat with ses=2)

* copy fmriprep/...confounds
do rsync -rvz /Volumes/mrenkeED/data/ds-stressrisk/derivatives/fmriprep/sub-${sub}/ses-${ses}/func/*_desc-confounds_timeseries.tsv sciencecloud2:/mnt/ds-stressrisk/derivatives/fmriprep/sub-${sub}/ses-${ses}/func ; done;

* events.txt to sciencecloud
    * do rsync -rcvz /Volumes/mrenkeED/data/ds-stressrisk/derivatives/spm/sub-${sub} sciencecloud2:/mnt/ds-stressrisk/derivatives/spm; done;
    * do for ses in 1 2; do rsync -avz --include='*/' --include='*NLCn.txt' --exclude='*' /Volumes/mrenkeED/data/ds-stressrisk/derivatives/spm/sub-${sub}/ses-${ses}/ sciencecloud2:/mnt/ds-stressrisk/derivatives/spm/sub-${sub}/ses-${ses}; done; done;
    * do for ses in 1 2; do rsync -rcvz /Volumes/mrenkeED/data/ds-stressrisk/derivatives/spm/sub-${sub}/ses-${ses}/event_files sciencecloud2:/mnt/ds-stressrisk/derivatives/spm/sub-${sub}/ses-${ses}; done; done;

14 34 40 41 57
# sync back SPMs from sciencecloud2 to local/ED

* 2ndLevel-SPM folders: 
rsync -avzr --include='2ndlevel_*/' --exclude='*/' sciencecloud2:/mnt/ds-stressrisk/derivatives/spm/ /Volumes/mrenkeED/data/ds-stressrisk/derivatives/spm

rsync -avzr --include='1stlevel_*/' --exclude='*.*' sciencecloud2:/mnt/ds-stressrisk/derivatives/spm/sub-${sub}/ses-${ses}/ /Volumes/mrenkeED/data/ds-stressrisk/derivatives/spm/sub-${sub}/ses-${ses}

* 1stlevel back to /Volumes to make space on /mnt
--> loop ofer sub, ses, model
rsync -rcvz sciencecloud2:/mnt/ds-stressrisk/derivatives/spm/sub-${sub}/ses-${ses}/1stlevel_${model} /Volumes/mrenkeED/data/ds-stressrisk/derivatives/spm/sub-${sub}/ses-${ses}

for sub in 01 02 03 04 05 09 10 12 13 14 16 17 18 19 21 22 23 24 25 26 28 30 31 32 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 57 58 59 61; do for ses in 1 2; do rsync -rcvz sciencecloud2:/mnt/ds-stressrisk/derivatives/spm/sub-${sub}/ses-${ses}/1stlevel_${model} /Volumes/mrenkeED/data/ds-stressrisk/derivatives/spm/sub-${sub}/ses-${ses}; done; done;

* mv folders around on sciencecloud in loops !! 
for sub in 01; do cd /mnt/ds-stressrisk/derivatives/spm/sub-${sub}; for ses in 1 2; do  mv ses-${ses}/fwhm-* .;  done; done;

for sub in 02; do cd /mnt/ds-stressrisk/derivatives/spm/sub-${sub}; for ses in 1 2; do  mv ./fwhm-8_sub-${sub}_ses-${ses}* ses-${ses}/;  done; done;

# prepare 
 fslmaths in-file.nii -nan out-file 

# working on the clluster:
* check which jobs finished/failed on which nodes: sacct -S '2023-06-14' -u mrenke -o jobid%25,start,exitcode,nodelist%25,state
* exclude nodes that dont work: --exclude=u20-computeibmgpu-vesta19
* 02,03,04,05,14,16,17,18,19,21,22,23,24,25,37,38,45,46,47,52,53,54,58,59


# problems

* glm_denoise --retroicor (--smoothed) failed on sciencecluster (03,18,44 ses-1; 04 ses-2), 03 (input NaNs) & 04 (Matrix singular) worked on local 


# Surface Visualization

 %run visualize_nPRFmodel_subject.py 2 --fsnative --key encoding_model.denoise.retroicor.smoothed

 # MRIY
 * on sciencecloud3 : 
 
    sudo docker run -it --rm -v /mnt/ds-stressrisk:/data:ro -v /mnt/ds-stressrisk/derivatives/mriqc:/out nipreps/mriqc:latest /data /out participant --participant_labels 01 02 03 04 05 09 10 12 13 14 16 17 18 19 21 22 23 24 25 26 28 30 31 32 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 57 58 59 61
* on sciencecluster:
    srun --pty -n 1 -c 2 --time=02:30:00 --mem=7G bash -l
    module load singularityce # some nodes have it, some not (e.g. compute-m6)
    
    singularity build --sandbox /data/mrenke/mriqc-23.1.0.simg docker://nipreps/mriqc:23.1.0 # from https://hub.docker.com
    singularity run --cleanenv /data/mrenke/mriqc-23.1.0.simg /shares/zne.uzh/mrenke/ds-stressrisk /shares/zne.uzh/mrenke/ds-stressrisk/derivatives/mriqc group -w /scratch/mrenke/workflow_folders/mriqc # does not work, but 
    
    singularity run --cleanenv /data/mrenke/mriqc-23.1.0.simg /shares/zne.uzh/$USER/ds-stressrisk /shares/zne.uzh/$USER/ds-stressrisk/derivatives/mriqc participant -w /scratch/mrenke/workflow_folders/mriqc --participant_label 02
    * * errors:
        * * * OSError: Error occurred while trying to decode JSON from file /shares/zne.uzh/mrenke/ds-stressrisk/sub-02/ses-1/func/._sub-02_ses-1_task-risk_run-1_bold.json --> delete those files (that somehow probably got creted, code in `/Users/mrenke/git/stress_risk/stress_risk/prepare/correct_json-file_task.ipynb`)
        * * * ModuleNotFoundError: No module named 'niworkflows.interfaces.utils' --> 
    * * Traceback (most recent call last):
        File "/opt/conda/bin/mriqc", line 8, in <module>
            sys.exit(main())
        File "/opt/conda/lib/python3.9/site-packages/mriqc/cli/run.py", line 206, in main
            dataframe, out_tsv = generate_tsv(output_dir, mod)
        File "/opt/conda/lib/python3.9/site-packages/mriqc/utils/misc.py", line 181, in generate_tsv
            jsonfiles = list(output_dir.glob("sub-*/**/%s/sub-*_%s.json" % (IMTYPES[mod], mod)))
        KeyError: 'dwi'


    singularity run -u -B /shares/zne.uzh/$USER/ds-stressrisk:/data -B /shares/zne.uzh/$USER/ds-stressrisk/derivatives/mriqc:/out /data/mrenke/nipreps /data /out participant --participant_labels 01
