
# for plotting surface map
from brainspace.utils.parcellation import map_to_labels
from  nilearn.datasets import fetch_surf_fsaverage
import nilearn.plotting as nplt
import matplotlib.pyplot as plt
from utils import get_basic_mask
from nilearn import datasets
import numpy as np
import os.path as op
from nilearn import image, plotting, surface

def plot_GM123_from_sum_npfile(file = 'gm_av50_unfiltered_aligned-marg.npy',bids_folder='/Volumes/mrenkeED/data/ds-stressrisk',
                              view='medial',grad_folder = 'derivatives/gradients', colorbar=False):

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

    plotting.plot_surf(
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