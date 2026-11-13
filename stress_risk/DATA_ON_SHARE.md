# Data on the department share — reproducing the paper

Everything needed to reproduce the paper figures and statistics from this repo is on
the UZH econ department share. This file says what is there, how it is laid out, and
**how to assemble it into the folder the code expects**, which is not the same shape.

```
/Volumes/g_econ_department$/projects/2022/renkert_dehollander_aydogan_ruff_stressrisk/data/
```

Verified complete on 2026-09-01.

---

## The two folders

The dataset is split in two, for a reason that matters when you copy it:

| Folder | Contents |
| --- | --- |
| `ds-stressrisk_openNeuro/` | The **raw BIDS dataset** as published: defaced anatomicals, functional `bold.nii`, fieldmaps, `dataset_description.json`. |
| `ds-stressrisk_remaining/` | Everything *not* in the public release: behavioural `events.tsv`, physio logs, all `derivatives/`, model traces, and the summary CSVs. |

Neither is a working analysis folder on its own — the code expects a **single**
`ds-stressrisk` root containing both. See *Reconstruction* below.

Also present at that level and **not needed for the paper**: `deface_freesurfer/`,
`logs/`, `sourcedata/`, `wrapper-data/`, and the per-subject `*_deface.log` files.

---

## `ds-stressrisk_remaining/` layout

```
ds-stressrisk_remaining/
├── group_assignmentList.csv          # subject → group (0 = control, 1 = stress)
├── addMeasures/
│   ├── data_combined.xlsx            # used by utils.data.add_cond2df
│   ├── auc_cortisol.xlsx             # cortisol AUC (stress manipulation check)
│   ├── selfRated_Stress.csv          # per-subject mean self-rated stress
│   ├── selfRated_Stress_allMeasures.csv
│   └── AllRunsSummary.csv
├── sub-<NN>/ses-<1|2>/
│   ├── anat/   sub-NN_ses-1_{T1w,FLAIR}.nii
│   └── func/   *_events.tsv           # behaviour — the input to get_data()
│                *_value_events.tsv    # trialwise Vhat, for the value GLMs
│                *_physio.log          # cardiac/respiratory, input to RETROICOR
├── interim_sum_data/                 # FLAT - all 33 tables, see its own README.md
│   ├── within_ses_decodedE.csv       # ┐
│   ├── across_ses_decodedE.csv       # │ read by the paper notebooks
│   ├── within-ses-decod_r-sds.csv    # │
│   ├── HRV_var-v1_sampRate-500_subwise.csv  # │
│   ├── r-prior-shift_Ediff_AUC.csv   # ┘ (also read unconditionally by fit_bauerModels.py)
│   ├── subwise_change_prior_model-5.csv, commonPriorShift-model5_Ediff_AUC.csv,
│   ├── subwise_change_{risky,safe}_prior_model-1.csv,
│   ├── subwise_seswise_{motion,n1_evidence_sd,n2_evidence_sd}.csv, …   # additional analyses
│   └── encoding_params_*.csv, glm_table_*.csv, …                       # saved, never read back
├── derivatives/
│   ├── cogmodels/                    # fitted model traces (netcdf, 330 MB – 1.2 GB each)
│   ├── fmriprep/                     # preprocessed fMRI
│   ├── freesurfer/                   # surface reconstructions
│   ├── glm_stim1.denoise.retroicor/  # GLMsingle single-trial betas
│   ├── encoding_model.cv.denoise.retroicor/        # cross-validated nPRF fits
│   ├── encoding_model.{denoise.retroicor,cv.denoise.smoothed}/
│   ├── decoded_pdfs.volume.cv_voxel_selection.denoise.retroicor/   # within-session
│   ├── decoded_pdfs.volume.svoxels.ses1-en_ses2-de.denoise.retroicor/ # across-session
│   └── SPMs/{1stLevels,2ndLevel}/    # value GLMs (supplements / not in paper)
└── sourcedata/{behavior,mri}/        # pre-BIDS originals
```

---

## Reconstruction: building a working `ds-stressrisk`

Assemble both folders into one root, then point the code at it by editing
`BIDS_FOLDER` in `stress_risk/utils/data.py` (one line — see *Pointing the code at
your copy* below).

One thing differs from what the code expects: the raw BOLD lives in
`ds-stressrisk_openNeuro/` and everything else in `ds-stressrisk_remaining/`, so the
two have to be merged into a single root. Nothing else needs rearranging.

```bash
SHARE='/Volumes/g_econ_department$/projects/2022/renkert_dehollander_aydogan_ruff_stressrisk/data'
DEST=~/data/ds-stressrisk

mkdir -p "$DEST"
rsync -a "$SHARE/ds-stressrisk_remaining/"  "$DEST/"     # behaviour, derivatives, traces
rsync -a "$SHARE/ds-stressrisk_openNeuro/"  "$DEST/"     # raw BOLD, merges into sub-*/
```

Full copy is several hundred GB (fMRIPrep + FreeSurfer dominate). **For the paper
figures alone you do not need the imaging derivatives** — see the next section.

---

## Minimum set per notebook

### `paperFinal_allMainPlotsStatistics_.ipynb` — all main figures & statistics

| Needs | From |
| --- | --- |
| `sub-*/ses-*/func/*_events.tsv` | behaviour, for `get_data()` |
| `group_assignmentList.csv`, `addMeasures/data_combined.xlsx` | group assignment |
| `derivatives/cogmodels/bambi-RNP-fit_trace_model1.netcdf` | probit / RNP |
| `derivatives/cogmodels/model-5_trace.netcdf` | PMC model |
| `interim_sum_data/{within_ses_decodedE,across_ses_decodedE,within-ses-decod_r-sds}.csv` | neural shift & uncertainty |

**~1.1 GB.** No imaging derivatives needed — the decoding is already summarised in
those three CSVs.

### `paperFinal_supplements.ipynb`

Adds `model-5_noStress_trace.netcdf`, `model-EU_3_trace.netcdf`,
`model-EU_noStress__trace.netcdf` (model comparison), `addMeasures/auc_cortisol.xlsx`,
`addMeasures/selfRated_Stress.csv`, and
`interim_sum_data/HRV_var-v1_sampRate-500_subwise.csv`. **~3.5 GB total.**

### `brainBehav_commonPriorShift_vs_neuralShift.ipynb`

`model-5_trace.netcdf`, the two decoded-E CSVs, `group_assignmentList.csv`, and
`r-prior-shift_Ediff_AUC.csv` (for the AUC column).

### Re-running the neural pipeline from scratch

Only then do you need `derivatives/{fmriprep,freesurfer,glm_stim1.*,encoding_model.*,
decoded_pdfs.*}` — hundreds of GB, GPU cluster, days of compute. The step-by-step
chain is in [`plots_for_paper/README.md`](plots_for_paper/README.md) §4.

---

## Added 2026-09-01

These were missing from the share and have been copied up; without them the
supplements notebook and the HRV/stress-manipulation figures cannot run:

- `group_assignmentList.csv`
- `addMeasures/` (all 5 files, incl. `auc_cortisol.xlsx`)
- `interim_sum_data/paper_relevant_summaryData/HRV_var-v1_sampRate-500_subwise.csv`
- `interim_sum_data/add_summaryData/commonPriorShift-model5_Ediff_AUC.csv`
- `derivatives/cogmodels/model-5_noStress_trace.netcdf` (346 MB)
- `derivatives/cogmodels/model-EU_noStress__trace.netcdf` (887 MB)
- `derivatives/cogmodels/model-1_null_trace.netcdf` (311 MB) — the PMC null model,
  commented out in the supplements model comparison but there if wanted
- root: `dataset_description.json`, `task-risk_bold.json`,
  `StressRiskNum_ConditionAssigned*.csv`, and the `.numbers` source files

`interim_sum_data/` was **flattened** the same day: it had been split into
`paper_relevant_summaryData/` and `add_summaryData/`, but every read in the repo uses
a flat `interim_sum_data/<name>` path, so no code could find the files. The split had
also misfiled `r-prior-shift_Ediff_AUC.csv` — which `fit_bauerModels.py` reads
unconditionally — as "additional". The distinction is now recorded in
`interim_sum_data/README.md` on the share instead of in the folder structure.

Not copied: `model-EU_noStress_trace.netcdf` (0 bytes locally — a failed write; the
real file is `model-EU_noStress__trace.netcdf`, with two underscores).

## Pointing the code at your copy, and other things to know

1. **Point the code at your copy in one place.** `stress_risk/utils/data.py` defines

   ```python
   BIDS_FOLDER = '/Users/mrenke/data/ds-stressrisk'
   ```

   Every function in `utils/data.py`, `behavior/utils.py` and
   `analyse_results/utils.py` uses it as its default and still accepts an explicit
   `bids_folder=...`. The three notebooks in `plots_for_paper/` set their own
   `bids_folder` in the first cell, with the share path in a comment above it.
   Scripts take `--bids_folder`.

   The fMRI pipeline scripts under `fmri_analysis/` still default to `/data` — they
   are always given `--bids_folder` explicitly by the cluster submit scripts. Older
   exploratory code (`gradients/`, `old_scripts/`, `explore/`) was deliberately left
   with its hard-coded paths.

2. **Figure output goes to `~/Desktop/StressRisk/figures/plots/paper`** via
   `plot_folder_path`. Change it, or the `savefig` lines (currently commented out)
   will fail.
3. **50 subjects** have behavioural events on the share; the paper's neural analyses
   run on 49 (sub-01 has no session-2 decoding).
4. `derivatives/SPMs/` on the share is `derivatives/spm/` in the code.
