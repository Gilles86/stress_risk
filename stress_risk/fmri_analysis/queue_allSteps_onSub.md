##

subject='18';
session='1';

cd /Users/mrenke/git/stress_risk/stress_risk/prepare;

python convert_behavior.py $subject $session --bids_folder /Users/mrenke/data/ds-stressrisk

subject='19';
session='1';

cd /Users/mrenke/git/stress_risk/stress_risk/fmri_analysis;
python fit_single_trials.py $subject $session;
python fit_nprf.py $subject $session;
cd /Users/mrenke/git/stress_risk/stress_risk/fmri_analysis/surface;
python transform_npc.py $subject;
python npc_to_volume.py $subject;

cd /Users/mrenke/git/stress_risk/stress_risk/fmri_analysis;
session='1';
subject='03';
python fit_nprf.py $subject $session --smoothed;
python fit_task_crossVal.py $subject $session --smoothed;
python run_decoder.py $subject $session --smoothed;

subject='04';
python fit_task_crossVal.py $subject $session --smoothed;
python run_decoder.py $subject $session --smoothed;


for subject in 05 06 07 08 09 10 11 12 13 14; do python run_decoder.py $subject $session --smoothed; done; 


python fit_single_trials.py $subject $session --smoothed;
python fit_nprf.py $subject $session --smoothed;
python fit_task_crossVal.py $subject $session --smoothed;
python run_decoder.py $subject $session --smoothed;


for subject in 20 21 22 23 24 25 26 27 28 29 30; do python convert_raw_mri_data.py $subject 1 --bids_folder /Users/mrenke/data/ds-stressrisk ; done;

for subject in 20 21 22 23 24 25 26 27 28 29 30; do rsync -rcvz ~/data/ds-stressrisk/sub-$subject sciencecluster:/data/mrenke/ds-stressrisk; done;

sbatch --array=20,21,22,23,24,25,26,27,28,29,30 fmriprep.sh

on sciencecluster
for subject 21 23 24 25 26 27; do python fit_nprf.py $subject 1 --bids_folder /data/mrenke/ds-stressrisk --smoothed; done;


for subject in 22 23 24 25 26 27 28 29 30; do python transform_npc.py $subject --bids_folder /data/ds-stressrisk; done;
for subject in 31 33 34 35 36 37 38 39 40; do python transform_npc.py $subject --bids_folder /data/ds-stressrisk; done;

for subject in 22 23 24 25 26 27 28 29 30 31 33 34 35 36 37 38 39 40; do python npc_to_volume.py $subject --bids_folder /data/ds-stressrisk; done;


for subject in 41 42 43 44 45 46 47 48; do rsync -rcvz sciencecluster:/data/mrenke/ds-stressrisk/derivatives/fmriprep/sub-${subject}/ses-1/anat/sub-${subject}_ses-1_desc-preproc_T1w.nii.gz ~/data/ds-stressrisk/derivatives/fmriprep/sub-${subject}/ses-1/anat;done;

for subject in 22 ; do rsync -rcvz sciencecluster:/data/mrenke/ds-stressrisk/derivatives/fmriprep/sub-$subject/ses-1/anat/sub-$subject_ses-1_desc-preproc_T1w.nii.gz ~/data/ds-stressrisk/derivatives/fmriprep/ses-1/anat; done;

rsync -rcvz sciencecluster:/data/mrenke/ds-stressrisk/derivatives/fmriprep/sub-22/ses-1/anat/sub-22_ses-1_desc-preproc_T1w.nii.gz ~/data/ds-stressrisk/derivatives/fmriprep/sub-22/ses-1/anat



for subject in 41 42 43 44 45 46 47 48; do python fit_single_trials.py $subject 1 --smoothed --bids_folder /data/mrenke/ds-stressrisk ; done;

for subject in 41 42 43 44 45 46 47 48; do python fit_nprf.py $subject 1 --smoothed --bids_folder /data/mrenke/ds-stressrisk ; done;