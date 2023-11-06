import tensorflow as tf
with tf.device('/cpu:0'):
    from fugw.scripts import coarse_to_fine, lmds
from nilearn import datasets, image, plotting, surface
import argparse
import numpy as np
import os.path as op
from tensorflow.python.ops.numpy_ops import np_config
np_config.enable_numpy_behavior()

#tf.register_backend(TensorflowBackend())

bids_folder = '/Volumes/mrenkeED/data/ds-stressrisk'
grad_folder = 'derivatives/gradients'

def main():
    fsaverage5 = datasets.fetch_surf_fsaverage(mesh="fsaverage5")


    (coordinates, triangles) = surface.load_surf_mesh(fsaverage5.pial_left)
    fs5_pial_left_geometry_embeddings = lmds.compute_lmds_mesh(
        coordinates,
        triangles,
        n_landmarks=100,
        k=3,
        n_jobs=1,
        verbose=True,
    )

    np.save(op.join(bids_folder,grad_folder,'fs5_pial_left_geometry_embeddings.npy'),fs5_pial_left_geometry_embeddings)


if __name__ == '__main__':

    main()