

# Trying to have an overivew of all the sstuff I did related to gradients

### different techniques:

* no parcellation is meanwhile the standard (added `no_Parcel` )
* builtin - kernel & aligmnet (procrust) --> `fir_grad_only_aligned.py` kernel&align modifications, saves to np file 
* in fsnative space: takes way to much time....



### average (task!) gradient *check
* calculated correlation matrices for each subject on sciencecloud `gen_corr_matrix.py` (does not need to be filtered, effect of weird vertices seems to be removed by arctan+average)
* --> `avGrad_sciencecloud.py` reads in all CM from previous step, normalizes with arctan, average, --> fit GM
* `avGrad_local.py` inspect average_GM, ....

## alignment
--> fit_grad_all_reordMaskFlip.py

### reorder & flipping

* first tried procrust 
--> found out that the brainspace built in procrust alignment does work, was just reading the wrong part out of the fitted GM
[`gm.aligned_` vs. `gm.gradients_`]
* but with kernel=None filtering is still necessary!

### morphospace comparisons




