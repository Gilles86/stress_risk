# get sub lists for analysis steps

#%% 
from os import listdir
from os.path import isfile, join
import os

bids_folder = '/Users/mrenke/data/ds-stressrisk'
bids_folder = '/Volumes/mrenkeED/data/ds-stressrisk/derivatives/freesurfer'
#%%
subFolders = [f for f in listdir(bids_folder) if f[0:3] == 'sub']

l = str()
for e in subFolders:
    if len(e) == 6:
        l = l + e[4:] + ','

# %%
