##

## get data, convert behavior & MRI



## Step 0: fmriprep
* cluster/preprocess/fmriprep_mr.sh
## Step 1: fit the glm with glmdenoise (retroicor, smooth, pca-confounds)
* fmri_analysis/glm/cluster_scripts/submit_glm_mr.sh
## Step 2: fit encoding model with cv
* fmri_analysis/encoding_model/submit_cv_mr.sh
## Step 3 & 4 : get atlas NPC mask into individual space & get individual NPC mask in voxel space
* need freesurfer & fmriprep folder from preprocessing on sciencecloud
* fmri_analysis/surface/transform_npc.py [sub --bids_folder]
* fmri_analysis/surface/npc_to_volume.py [sub --bids_folder]

## Step 5: decoding (only --denoise )

## Step 6: fit standard logisitc (Woodford model) and obtain RNPs

## Step 7: check the decoding results, combine them with RNPs and write them to a tsv



# install all necessary packages

* `cd stress_risk`: `pip install --editable .`
* `cd GLMsingle`  
* needs: `pip install pyyaml`
* conda install -n behav_fit ipykernel --update-deps --force-reinstall

