# see where r2 responsive vertices lie in grad1 - grad2 morhpospace
# needs `....r2.surf.gii` from gradients/vis_gradients.py

# %%

import nilearn
import numpy as np
import nibabel as nib
import os.path as op
import pandas as pd

bids_folder = '/Users/mrenke/data/ds-stressrisk'

sub = '01' 
ses = 1

source_dir = op.join(bids_folder, 'derivatives', 'gradients', f'sub-{sub}', f'ses-{ses}')
mask_dir = op.join(bids_folder, 'derivatives', 'ips_masks', f'sub-{sub}')

#%%

grad1 = [None]*2
grad2 = [None]*2

for i, hemi in enumerate(['L', 'R']):
    grad1[i] = nib.load(op.join(source_dir, f'sub-{sub}_ses-{ses}_task-risk_space-fsnative_hemi-{hemi}_grad1_noParcel.surf.gii'))
    grad2[i] = nib.load(op.join(source_dir, f'sub-{sub}_ses-{ses}_task-risk_space-fsnative_hemi-{hemi}_grad2_noParcel.surf.gii'))


r2_L = nib.load(op.join(source_dir,f'sub-{sub}_ses-{ses}_task-risk_space-fsnative_hemi-L_r2.surf.gii'))
r2_R = nib.load(op.join(source_dir,f'sub-{sub}_ses-{ses}_task-risk_space-fsnative_hemi-R_r2.surf.gii'))

#%% mask if wanted

ips_L= nib.load(op.join(mask_dir, f'sub-{sub}_desc-NPC_L_space-fsnative_hemi-lh.ips.gii'))
ips_R= nib.load(op.join(mask_dir, f'sub-{sub}_desc-NPC_R_space-fsnative_hemi-rh.ips.gii'))

# %%

#  plot vertices' grad-values in 2D
import matplotlib.pyplot as plt
import matplotlib as mpl

grad1_ = np.concatenate([grad1[0].agg_data(), grad1[1].agg_data()])
grad2_ = np.concatenate([grad2[0].agg_data(), grad2[1].agg_data()])
r2 = np.concatenate([r2_L.agg_data(), r2_R.agg_data()])


ips_mask = np.concatenate([ips_L.agg_data(), ips_R.agg_data()])
# if t here is no ips_L.agg_data()
r_hemi_mask = ips_R.agg_data() #(137677,) ndarray
l_hemi_mask = [False] * (len(grad1_) - len(r_hemi_mask))
ips_mask = np.concatenate([l_hemi_mask, r_hemi_mask])

#r2[ips_mask == 0] = np.NaN

plt.scatter(grad2_, grad1_, s=0.1, c = r2, cmap = mpl.colormaps['hot'])
plt.axvline(x=0, color = 'black')
plt.axhline(y=0, color = 'black')
plt.show
#%% 
# only right [1] hemisphere
ips_R= nib.load(op.join(mask_dir, f'sub-{sub}_desc-NPC_R_space-fsnative_hemi-rh.ips.gii'))

grad1_ = grad1[1].agg_data()
grad2_ = grad2[1].agg_data()
r2 = r2_R.agg_data()

#ips_mask =  ips_R.agg_data()
#r2[ips_mask == 0] = np.NaN # add or rmove this line to look at only point lying within IPS-mask

plt.scatter(grad2_, grad1_, s=0.1, c = r2, cmap = mpl.colormaps['hot'])
plt.axvline(x=0, color = 'black')
plt.axhline(y=0, color = 'black')
plt.show

# %% Scatter plot with histograms

x = grad2_
y = grad1_

def scatter_hist(x, y, ax, ax_histx, ax_histy):
    # no labels
    ax_histx.tick_params(axis="x", labelbottom=False)
    ax_histy.tick_params(axis="y", labelleft=False)

    # the scatter plot:
    ax.scatter(x, y)
    ax.axvline(x=0, color = 'black')
    ax.axhline(y=0, color = 'black')


    # now determine nice limits by hand:
    binwidth = 0.25
    xymax = max(max(np.abs(x)), max(np.abs(y)))
    lim = (int(xymax/binwidth) + 1) * binwidth

    bins = np.arange(-lim, lim + binwidth, binwidth)
    ax_histx.hist(x, bins=bins)
    ax_histy.hist(y, bins=bins, orientation='horizontal')
    ax_histx.axvline(x=0, color = 'black')
    ax_histy.axhline(y=0, color = 'black')


# Start with a square Figure.
fig = plt.figure(figsize=(6, 6))
# Add a gridspec with two rows and two columns and a ratio of 1 to 4 between
# the size of the marginal axes and the main axes in both directions.
# Also adjust the subplot parameters for a square plot.
gs = fig.add_gridspec(2, 2,  width_ratios=(4, 1), height_ratios=(1, 4),
                      left=0.1, right=0.9, bottom=0.1, top=0.9,
                      wspace=0.05, hspace=0.05)
# Create the Axes.
ax = fig.add_subplot(gs[1, 0])
ax_histx = fig.add_subplot(gs[0, 0], sharex=ax)
ax_histy = fig.add_subplot(gs[1, 1], sharey=ax)

# Draw the scatter plot and marginals.
scatter_hist(x, y, ax, ax_histx, ax_histy)
# %%


# %% overlay of histograms
plt.hist(grad2_, bins = 1000)
plt.xlabel('grad2')
plt.axvline(x=0, color = 'black')
plt.show

plt.hist(grad1_, bins = 1000)
plt.xlabel('grad1')
plt.axvline(x=0, color = 'black')
plt.show
