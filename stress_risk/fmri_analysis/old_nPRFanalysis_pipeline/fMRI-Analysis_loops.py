#%% loop for running python scripts on subs
# errorL =   '03151617' from retrocoir

import os

os.chdir('/Users/mrenke/git/stress_risk/stress_risk/fmri_analysis')
#%%
sub_list_s = list(range(3,18))
sub_list= []
for e in sub_list_s:
    sub_list.append(str(e).zfill(2))

ses = 1 

# %%--------------------------------------------
import fit_single_trials

errList = []
for sub in sub_list:
    try:
        fit_single_trials.main(sub, ses,bids_folder='/Users/mrenke/data/ds-stressrisk', smoothed = True )
    except:
        errList.append(sub)
        
# errL = ['03','04','15','16',17']
# %%
import fit_nprf

errList_np = []
for sub in sub_list:
    try:
        fit_nprf.main(sub, ses,bids_folder='/Users/mrenke/data/ds-stressrisk', smoothed = True )
    except:
        errList_np.append(sub)

# errL = ['03','04','15','16',17']        
# %%
ses = 1
import fit_task_crossVal

errList_cv = []
for sub in sub_list:
    try:
        fit_task_crossVal.main(sub, ses,bids_folder='/Users/mrenke/data/ds-stressrisk', smoothed = True )
    except:
        errList_cv.append(sub)


# %%
# run all that for one specific subject
import run_decoder

errList_dc = []
for sub in sub_list:
    try:
        run_decoder.main(sub, ses,bids_folder='/Users/mrenke/data/ds-stressrisk', smoothed = True )
    except:
        errList_dc.append(sub)


# %%
