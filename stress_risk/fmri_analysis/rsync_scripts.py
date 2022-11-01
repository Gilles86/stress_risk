import os
import os.path as op

# do this:
# for subject in 22 23 24 25 26 27 28 29 30 31 33 34 35 36 37 38 39 40;
#   do rsync -rcvz 
#   sciencecluster:/data/mrenke/ds-stressrisk/derivatives/fmriprep/sub-$subject/ses-1/anat/sub-$subject_ses-1_desc-preproc_T1w.nii.gz 
#   ~/data/mrenke/ds-stressrisk/derivatives/fmriprep
# ; done;


bids_folder = '/Users/mrenke/data/ds-stressrisk'
ses = 1

sub_list_s = list(range(25,40+1))
sub_list= []
for e in sub_list_s:
    sub_list.append(str(e).zfill(2))


for sub in sub_list:
    target_folder = op.join(bids_folder, 'derivatives', 'fmriprep', f'sub-{sub}')
    os.makedirs(target_dir)