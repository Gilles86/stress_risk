
# for plotting surface map
from brainspace.utils.parcellation import map_to_labels
from  nilearn.datasets import fetch_surf_fsaverage
import matplotlib.pyplot as plt
from utils import get_basic_mask
from nilearn import datasets
import numpy as np
import os.path as op
#from nilearn import image, plotting, surface
import nilearn.plotting as nplt

def plot_GM123_from_sum_npfile(file = 'gm_av50_unfiltered_aligned-marg.npy',bids_folder='/Volumes/mrenkeED/data/ds-stressrisk',
                              view='medial',grad_folder = 'derivatives/gradients', 
                              colorbar=False):

    mask, labeling_noParcel = get_basic_mask()
    fsaverage = fetch_surf_fsaverage()

    gm = np.load(op.join(bids_folder,grad_folder,file))
    
    grad = [None] * np.shape(gm)[1]
    for i, g in enumerate(gm.T):
        grad[i] = map_to_labels(g, labeling_noParcel, mask=mask, fill=np.nan)

    grad1 = np.split(grad[0],2) # for i, hemi in enumerate(['L', 'R']): --> left first
    grad2 = np.split(grad[1],2)
    grad3 = np.split(grad[2],2)
    
    grad1_r = grad1[1] # 0 = left, 1 = right
    grad2_r = grad2[1]  
    grad3_r = grad3[1]

    figure, axes = plt.subplots(nrows=1, ncols=3, subplot_kw=dict(projection='3d'))
    nplt.plot_surf_stat_map(surf_mesh=fsaverage.infl_right, colorbar = colorbar,stat_map=grad1_r,cmap='viridis',view=view,axes=axes[0])
    axes[0].set(title='grad 1')
    nplt.plot_surf_stat_map(surf_mesh=fsaverage.infl_right, colorbar = colorbar,stat_map=grad2_r,cmap='viridis',view=view,axes=axes[1])
    axes[1].set(title='grad 2')
    nplt.plot_surf_stat_map(surf_mesh=fsaverage.infl_right, colorbar = colorbar,stat_map=grad3_r,cmap='viridis',view=view,axes=axes[2])
    axes[2].set(title='grad 3')
    figure.suptitle(file)
    
def plot_from_nparray(grad, colorbar=False):
    
    fsaverage = fetch_surf_fsaverage()
    grad1 = np.split(grad[0],2) # for i, hemi in enumerate(['L', 'R']): --> left first
    grad2 = np.split(grad[1],2)
    grad3 = np.split(grad[2],2)
    
    grad1_r = grad1[1] # 0 = left, 1 = right
    grad2_r = grad2[1]  
    grad3_r = grad3[1]

    figure, axes = plt.subplots(nrows=1, ncols=3, subplot_kw=dict(projection='3d'))
    nplt.plot_surf_stat_map(surf_mesh=fsaverage.infl_right, colorbar = colorbar,stat_map=grad1_r,cmap='viridis',view='medial',axes=axes[0])
    axes[0].set(title='grad 1')
    nplt.plot_surf_stat_map(surf_mesh=fsaverage.infl_right, colorbar = colorbar,stat_map=grad2_r,cmap='viridis',view='medial',axes=axes[1])
    axes[1].set(title='grad 2')
    nplt.plot_surf_stat_map(surf_mesh=fsaverage.infl_right, colorbar = colorbar,stat_map=grad3_r,cmap='viridis',view='medial',axes=axes[2])
    axes[2].set(title='grad 3')
    #figure.suptitle(file)

def plot_surface_map(surface_map, fsaverage, cmap="coolwarm", colorbar=True, **kwargs):
    """Util function for plotting surfaces."""

    nplt.plot_surf(
        fsaverage.pial_left,
        surface_map,
        cmap=cmap,
        colorbar=colorbar,
        bg_map=fsaverage.sulc_left,
        bg_on_data=True,
        darkness=0.5,
        **kwargs,
    )



def align_gradients(gradients, reference):
    # Compute dot products
    gradients = np.array(gradients)
    reference_grad = np.array(reference)

    non_nan_indices = ~np.isnan(reference_grad[0])
    reference = reference_grad[:, non_nan_indices]
    gradients = gradients[:, non_nan_indices]

    dot_products = np.array([[np.dot(g, r) for r in reference] for g in gradients])
    print(dot_products)
    
    # Find the index of the reference gradient with the highest absolute dot product for each gradient
    max_dot_product_indices = np.argmax(np.abs(dot_products), axis=1)
    print(max_dot_product_indices)
    
    # Reorder gradients based on the index of the reference gradient with the highest absolute dot product
    gradients = gradients[np.argsort(max_dot_product_indices)]
    dot_products = np.array([[np.dot(g, r) for r in reference] for g in gradients]) # now the diagonal has the values for the matching gradients

    # Flip gradients where the dot product with the corresponding reference gradient is negative
    for i in range(np.shape(gradients)[0]):
        if dot_products[i,i] < 0:
            gradients[i] *= -1

    # re-insert nans
    nan_array = np.full(np.shape(reference_grad), np.nan)
    nan_array[:, non_nan_indices] = gradients
    gradients = nan_array
    
    return gradients


# better version (from looking at first 5 subjects)
# put first version (inspired by copilot) in utils_02.py

from nilearn import datasets

def align_gradients_ROIdependant(gradients, reference): # this version does not bother about nan values
    gradients = np.array(gradients)
    reference_grad = np.array(reference)

    # get masks
    atlas = datasets.fetch_atlas_surf_destrieux()
    labeling = np.concatenate([atlas['map_left'], atlas['map_right']]) # table with regions and names: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2937159/

    motor_mask = np.isin(labeling, atlas.labels.index(b'G_precentral')) 
    occ_mask = np.isin(labeling, atlas.labels.index(b'Pole_occipital'))
    atlats_index_highOrder = [atlas.labels.index(b'S_temporal_sup'), atlas.labels.index(b'S_interm_prim-Jensen')] # temporal, TPJ
    atlats_index_lowOrder = [atlas.labels.index(b'G_precentral'), atlas.labels.index(b'Pole_occipital' )] # motor, visual
    highOrderRegions_mask = np.isin(labeling, atlats_index_highOrder)
    lowOrderRegions_mask = np.isin(labeling, atlats_index_lowOrder)

    difs = np.zeros(shape = (3,2))
    for grad_n in range(3):
        dif_forgrad1 = gradients[grad_n][highOrderRegions_mask].mean() - gradients[grad_n][lowOrderRegions_mask].mean()
        dif_forgrad2 = gradients[grad_n][motor_mask].mean() - gradients[grad_n][occ_mask].mean()
        difs[grad_n,:] = [np.abs(dif_forgrad1), np.abs(dif_forgrad2)]
    print(difs)
    max_difs_masks_indices = np.argmax(np.abs(difs), axis=0)
    print(max_difs_masks_indices) # should work from inspecting the difs * , max_difs

    # assign the missing gradient   
    all_numbers = set(range(3))
    missing_number = all_numbers - set(max_difs_masks_indices)
    max_difs_masks_indices = np.append(max_difs_masks_indices, missing_number.pop())
    print(max_difs_masks_indices)  

    max_difs_masks_indices = np.array(max_difs_masks_indices, dtype=int).flatten()
    # Reorder gradients based on the index of the reference gradient with the highest absolute dot product
    gradients = gradients[np.argsort(max_difs_masks_indices), :]
    dot_products = np.array([[np.nansum(g * r) for r in reference] for g in gradients]) # kind of np.dot, but ignoring nans
    
    print(dot_products)
    # Flip gradients where the dot product with the corresponding reference gradient is negative
    for i in range(np.shape(gradients)[0]):
        if dot_products[i,i] < 0:
            gradients[i] *= -1

    return gradients

def get_reference_gradient(file = 'gm_av50_unfiltered_aligned-marg.npy',
                           bids_folder='/Volumes/mrenkeED/data/ds-stressrisk',
                           grad_folder = 'derivatives/gradients'):
    
    mask, labeling_noParcel = get_basic_mask()

    # reference 
    gm = np.load(op.join(bids_folder,grad_folder,file))
    grad = [None] * np.shape(gm)[1]
    for i, g in enumerate(gm.T):
        grad[i] = map_to_labels(g, labeling_noParcel, mask=mask, fill=np.nan)

    reference_grad = grad
    return reference_grad


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

import matplotlib.colors as colors

def get_GMmargulies_cmap(): 
    cmap = plt.get_cmap('nipy_spectral')
    new_cmap = truncate_colormap(cmap, 0.2, 0.95)

    #colors1 = plt.cm.YlGnBu(np.linspace(0, 1, 128))
    first = int((128*2)-np.round(255*(1.-0.90)))
    second = (256-first)
    #colors2 = new_cmap(np.linspace(0, 1, first))
    colors2 = plt.cm.viridis(np.linspace(0.1, .98, first))
    colors3 = plt.cm.YlOrBr(np.linspace(0.25, 1, second))
    colors4 = plt.cm.PuBu(np.linspace(0., 0.5, second))
    #colors4 = plt.cm.pink(np.linspace(0.9, 1., second))
    # combine them and build a new colormap
    cols = np.vstack((colors2,colors3))
    mymap = colors.LinearSegmentedColormap.from_list('my_colormap', cols)
    return mymap
# from : /Users/mrenke/git/gradient_analysis/03_visualize_embeddings.ipynb

