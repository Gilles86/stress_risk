import os
import os.path as op
import argparse
from neural_priors.utils.data import Subject, get_all_subject_ids
from tqdm.contrib.itertools import product
import pandas as pd
from stress_risk.utils.data import Subject
from nilearn.maskers import NiftiMasker
from nilearn import image

def get_vselect_mask(sub, bids_folder):
    roi='NPC_R'
    source_key_vselect = 'encoding_model.cv.denoise.retroicor'
    session1 = 1
    subject = Subject(int(sub), bids_folder=bids_folder)
    ips_mask = subject.get_volume_mask(roi=roi, session=1, epi_space=True) # anat from session1
    ips_masker = NiftiMasker(mask_img=ips_mask)
    im_cvr2_fn = op.join(bids_folder, 'derivatives', source_key_vselect, f'sub-{sub}', f'ses-{session1}','func', f'sub-{sub}_ses-{session1}_desc-cvr2.optim_space-T1w_pars.nii.gz')
    im_cvr2 = image.load_img(im_cvr2_fn)
    cv_r2 = pd.DataFrame(ips_masker.fit_transform(im_cvr2))
    r2_mask = cv_r2 > 0.0
    r2_mask = r2_mask.to_numpy().flatten()
    print(f'Number of voxels: {r2_mask.sum()}')
    return r2_mask, ips_masker

    
def get_prf_parameters_volume2(sub,bids_folder, model_label, smoothed=True, roi=None):

    par_keys = ['mu', 'sd','amplitude', 'baseline']

    # Create target folder
    key = f'model{model_label}'
    cv_key = key + '.cv'

    if smoothed:
        key += '.smoothed'
        cv_key += '.smoothed'

    masker = self.get_volume_mask(roi=roi, epi_space=True, return_masker=True)

    target_dir = op.join(self.bids_folder, 'derivatives', 'encoding_models2', key, f'sub-{sub}', 'func')

    pars = []

    for par, condition in product_(par_keys, ['ses', 'wide']):
        fn = op.join(target_dir, f'sub-{sub}_desc-{par}.{condition}.optim_space-T1w_pars.nii.gz')

        pars.append(pd.Series(masker.transform(fn).squeeze(), name=(par, condition)))

    pars.append(pd.Series(masker.transform(op.join(target_dir, f'sub-{sub}_desc-r2.optim_space-T1w_pars.nii.gz')).squeeze(), name=('r2', None)))

    cv_dir = op.join(self.bids_folder, 'derivatives', 'encoding_models2',  cv_key, f'sub-{sub}', 'func')

    pars.append(pd.Series(masker.transform(op.join(cv_dir, f'sub-{sub}_desc-cvr2.optim_space-T1w_pars.nii.gz')).squeeze(), name=('cvr2', None)))

    return pd.concat(pars, axis=1, names=['parameter', 'range'])



def main(roi='NPC_R', bids_folder='/mnt_01/ds-stressrisk', smoothed=True, fit_responses=False):

    key = 'encoding_models2'

    target_dir = op.join(bids_folder, 'derivatives', key)
    print(f'Writing to {target_dir}')
    os.makedirs(target_dir, exist_ok=True)

    subject_ids = get_all_subject_ids()
    model_labels = list(range(0, 9))
    subjects = [Subject(subject_id=subject_id) for subject_id in subject_ids]
    pars = []

    keys = []
    for sub, model_label, smoothed in product(subjects, model_labels, [True]):
        try:
            pars.append(get_prf_parameters_volume2(sub, bids_folder,model_label=model_label, smoothed=smoothed,  roi=roi))
            keys.append((sub.subject_id, model_label, smoothed))
        except Exception as e:
            print(f"Failed for {sub.subject_id} model {model_label}: {e}")

    pars = pd.concat(pars, keys=keys, names=['subject_id', 'model_label', 'smoothed'])
    pars.columns.names = ['parameter', 'range']
    pars.to_csv(op.join(target_dir, f'group_roi-{roi}_parameters.tsv'), sep='\t')



if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('roi', default='NPCr', type=str)
    argparser.add_argument('--bids_folder', default='/mnt_01/ds-stressrisk')
    argparser.add_argument('--fit_responses', action='store_true')

    args = argparser.parse_args()

    main(roi=args.roi, bids_folder=args.bids_folder, fit_responses=args.fit_responses)
