## tried it out, takes way to long

# "cc = connected_components(graph)" more than 40 mins !!

import argparse
from nilearn.connectome import ConnectivityMeasure
from brainspace.gradient import GradientMaps
from brainspace.utils.parcellation import map_to_labels
import numpy as np
import nibabel as nib
from nilearn import datasets
import os.path as op
import os
from nilearn import signal
import pandas as pd
from scipy.sparse.csgraph import connected_components
from utils import fsavTofsav5,cleanTS, saveGradToNPFile, npFileTofs5Gii,fsav5Tofsnative


def main(sub,ses,bids_folder,specification):