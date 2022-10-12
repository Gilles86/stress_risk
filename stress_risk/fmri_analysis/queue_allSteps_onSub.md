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