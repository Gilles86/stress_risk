# Paper figures & statistics — StressRisk

Everything that ended up in the paper is produced by the **three notebooks in this
folder**. Older, superseded drafts live in [`archive/`](archive/) — see
[`archive/README.md`](archive/README.md) for what each one was.

Analyses we ran but that did **not** make the paper (useful when a reviewer asks
for something extra) are indexed in [`../ADDITIONAL_ANALYSES.md`](../ADDITIONAL_ANALYSES.md).

**Reproducing this from the department share:** [`../DATA_ON_SHARE.md`](../DATA_ON_SHARE.md)
lists what data is where and the minimum file set each notebook needs.

---

## What is in this folder

| File | Role |
| --- | --- |
| `paperFinal_allMainPlotsStatistics_.ipynb` | **All main figures + all main statistics** reported in the paper. |
| `paperFinal_supplements.ipynb` | **All supplementary figures & tables** (PMC parameter table, model comparison, stress-manipulation checks, HRV). |
| `vis_nPRFmodel_3d.ipynb` | 3D plotly probability-surface illustration of the nPRF / braincoder encoding model. |
| `brainBehav_commonPriorShift_vs_neuralShift.ipynb` | **Not in the paper** — reviewer-response analysis: common prior shift (model 5) vs. shift in neural coding. See [`../ADDITIONAL_ANALYSES.md`](../ADDITIONAL_ANALYSES.md) §1. |
| `utils.py` | Plot helpers used by the main notebook (`plot_bayesian_inference`, `annotat_bayesian_inference`) — the PMC model schematic. |

Imported as a bare `from utils import ...`, so **the notebooks must be run with
this directory as the working directory.**

---

## Main notebook → figure/statistic map

`paperFinal_allMainPlotsStatistics_.ipynb`, in notebook order.

| Section | Produces | Reads |
| --- | --- | --- |
| Probit → *RNP & psychometric curve illustration* | `probit-model_illustration_01.pdf` (schematic, no data) | — |
| Probit → *Posterior distributions of effect sizes* | `probit-model_diffinsessions_violin.pdf`; RNP & slope difference-in-difference stats, absolute RNP per group×session, raw slope session/group effects | `derivatives/cogmodels/bambi-RNP-fit_trace_model1.netcdf` |
| Probit → *posterior predictive checks* | `probit-1_ppc.pdf` | same trace |
| PMC → *model illustration* | `NLC-model_illustration_01.pdf` | `utils.py` (schematic, no data) |
| PMC → *Posterior distributions of effect sizes* | `NLC-5-post_stres-control_violin.pdf`; prior-mu / n1- / n2-evidence-sd effects, per-group session differences and the group×session interaction | `derivatives/cogmodels/model-5_trace.netcdf` |
| PMC → *posterior predictive check* | `NLC-ppc_.pdf` | same trace, re-built model |
| Neural → *shift neural coding* | `shift-neural-coding_swarm-bar-plot_groups.pdf`; two-sample and one-sample t-tests on `E_dif`, risky/safe split, outlier-removed control | `interim_sum_data/within_ses_decodedE.csv`, `interim_sum_data/across_ses_decodedE.csv` |
| Neural → *neural uncertainty* | `shift_decodability-r_catplot-groups.pdf`; group t-test on the session change in decodability `r` | `interim_sum_data/within-ses-decod_r-sds.csv` |

Note: **all `plt.savefig` lines in the final notebooks are commented out** — uncomment
to regenerate. Output goes to `plot_folder_path`
(`~/Desktop/StressRisk/figures/plots/paper`), i.e. outside the repo and outside the
BIDS tree.

### Supplements notebook

| Section | Produces | Reads |
| --- | --- | --- |
| PMC parameter table | Absolute posterior means + 95% CI per parameter × group × session (`risky/safe_prior_mu`, `n1/n2_evidence_sd`, `risky/safe_prior_std`) | `derivatives/cogmodels/model-5_trace.netcdf` |
| Prior-std regressors | session / session:group effects on `risky_prior_std`, `safe_prior_std` | same trace |
| *Model comparison* | `model_comparison_all.png` — `az.compare` ELPD over PMC, PMC-no-stress, EU, EU-no-stress | `model-5_trace`, `model-5_noStress_trace`, `model-EU_3_trace`, `model-EU_noStress__trace` |
| *Stress manipulation effect* | Cortisol AUC + self-rated stress bar/swarm, group t-tests | `auc_cortisol.xlsx` (via `analyse_results.utils.get_stress_level`), `addMeasures/selfRated_Stress.csv` |
| *HRV measures* | `HRV_group_diffs_session-2.png`, `HRV_group_diffs_session-diff.png` — HR, SDNN, RMSSD, LF/HF; normality test then t-test or Mann-Whitney | `interim_sum_data/HRV_var-v1_sampRate-500_subwise.csv`, `group_assignmentList.csv` |

---

## Where the inputs come from

Everything the two `paperFinal_*` notebooks read is listed below with the code that
produced it. Order = order you would have to run it in.

### 0. Data preparation & preprocessing

Operational log with the actual commands: [`../analysis_pipeline_StressRisk.md`](../analysis_pipeline_StressRisk.md).

| Step | Code |
| --- | --- |
| Raw MRI → BIDS | `prepare/convert_raw_mri_data.py <sub> <ses>` |
| Behavior logs → BIDS events | `prepare/convert_behavior.py <sub> <ses>` |
| fMRIPrep | `cluster_preprocess/fmriprep.sh` (SLURM array) |
| RETROICOR physio confounds | `physiology/loop_prep_retrocoir.m` → `prepare_retroicor.m` (MATLAB/TAPAS) |

### 1. Behavior → `df`

`stress_risk.utils.data.get_data(bids_folder)` assembles all trials from the BIDS
events files. Group assignment comes from `addMeasures/data_combined.xlsx` via
`add_cond2df`, or from `group_assignmentList.csv` via `get_group_mapping`.

### 2. Probit model → `bambi-RNP-fit_trace_model1.netcdf`

Fitted **inside the main notebook** (the fit + `az.to_netcdf` lines are commented
out; only the load runs):

```
chose_risky ~ x*session*group + (x*session|subject)     # probit link, bernoulli
```

RNP and slope are extracted with `stress_risk.behavior.utils.extract_rnp_precision`,
then `rnp = clip(exp(intercept/gamma), 0, 1)`.

### 3. PMC model (formerly "NLC") → `model-*_trace.netcdf`

```bash
cd stress_risk/behavior
python fit_bauerModels.py 5              # the PMC model reported in the paper
python fit_bauerModels.py 5_noStress     # supplement: model comparison
python fit_bauerModels.py EU_3           # supplement: expected-utility model
python fit_bauerModels.py EU_noStress    # supplement: model comparison
```

Model specifications live in `behavior/utils.py::build_model`. Model `5` is
`RiskRegressionModel` with a **common prior shift**:

```python
regressors={'n1_evidence_sd':'session*group', 'n2_evidence_sd':'session*group',
            'prior_mu':'0 + session*group',
            'risky_prior_std':'session*group', 'safe_prior_std':'session*group'}
prior_estimate='full'
```

> `fit_bauerModels.py` also joins `interim_sum_data/r-prior-shift_Ediff_AUC.csv` to
> support the `--AUC` / `--E_dif` variants. That file is **not** needed for the
> paper models, but the script will fail without it — see *Rough edges* below.

### 4. Neural pipeline → decoded posteriors

Run per subject on the cluster; SLURM wrappers in each `cluster_scripts/` folder.

| Step | Script | Submit script | Writes to `derivatives/` |
| --- | --- | --- | --- |
| 1. Single-trial betas (GLMsingle) | `fmri_analysis/glm/fit_glm_denoise.py <sub> <ses> --smoothed` | `glm/cluster_scripts/submit_glm_mr.sh` | `glm_stim1.denoise…` |
| 2. Individual NPC/IPS mask | `fmri_analysis/surface/transform_npc.py <sub>` then `npc_to_volume.py <sub>` | — (local, needs FreeSurfer + fMRIPrep outputs) | `NPC_masks/`, volume mask |
| 3. Encoding model, cross-validated | `fmri_analysis/encoding_model/fit_model_cv.py <sub> <ses> --denoise` | `encoding_model/cluster_scripts/submit_cv_mr.sh` | `encoding_model.cv.denoise…` |
| 4a. **Within**-session decoding | `encoding_model/decode_select_voxels_cv.py <sub> 2 --mask NPC*_R --denoise --retroicor` | `submit_decode_select_voxels_cv.sh` | `decoded_pdfs.volume.cv_voxel_selection.denoise.retroicor` |
| 4b. **Across**-session decoding (encode ses-1 → decode ses-2) | `encoding_model/decode_svoxels.py <sub> --mask NPC*_R --denoise --retroicor` | `submit_decode_en1de2.sh` | `decoded_pdfs.volume.svoxels.ses1-en_ses2-de.denoise.retroicor` |

### 5. Decoded posteriors → the three summary CSVs the paper notebook reads

| CSV in `interim_sum_data/` | Written by | How |
| --- | --- | --- |
| `within_ses_decodedE.csv` | `analyse_results/decode_ana_01.ipynb` | Loops `analyse_results/utils.py::get_decoding_info` over subjects × sessions; per trial computes posterior mean `E` and spread `sd` over the presented numerosity range (log 5 … log 112). |
| `within-ses-decod_r-sds.csv` | `analyse_results/decode_ana_01.ipynb` | Per subject × session: `pingouin.corr(E, log(n1))` → **decodability `r`**, plus mean `sd`. |
| `across_ses_decodedE.csv` | `analyse_results/decode_ses1-en_ses2-de_ana.ipynb` | Same `E`/`sd` extraction on the ses1-encode → ses2-decode posteriors. |

The paper's **shift in neural coding** is then `E_dif = E_across − E_within`
(session 2 only), computed in the main notebook.

The **shift in neural uncertainty** is the session-1 minus session-2 difference in
decodability `r`.

### 6. Additional measures (supplements)

| Input | Written by |
| --- | --- |
| `addMeasures/selfRated_Stress.csv` (+ `_allMeasures.csv`) | `add_measures/stress_measures.ipynb` |
| `interim_sum_data/HRV_var-v1_sampRate-500_subwise.csv` | `add_measures/physio_hrv_loops.ipynb` (neurokit2; method development in `physio_hrv_ANS.ipynb`) |
| `auc_cortisol.xlsx` | Outside the repo — assay results, read by `analyse_results/utils.py::get_stress_level` |
| `interim_sum_data/subwise_seswise_motion.csv` | `add_measures/motion_confounds.ipynb` (motion control, not in the paper) |

### 7. Brain-surface visualisations

| Figure | Code |
| --- | --- |
| nPRF parameters on the inflated surface (sub-59) | `fmri_analysis/surface/visualize_nPRFmodel_sub59.py` — pycortex webgl; reads `derivatives/nifiti_toVisualize/sub-59/ses-1/func/*desc-{mu,sd,r2}.optim.nilearn_space-fsnative_hemi-{L,R}.func.gii` |
| Sampling nPRF params to surface (prerequisite) | `fmri_analysis/surface/sample_nPRFparams_to_surf.py`, `import_fs_sub_pycortex.py` |
| 3D encoding-model probability surface | `plots_for_paper/vis_nPRFmodel_3d.ipynb` (plotly; export the shown camera angle with the camera icon or `py.write_image`) |

---

## Environments

Two conda environments are used, and it matters which:

* **`numrefields`** — braincoder / TensorFlow GPU work: the encoding and decoding
  scripts. On the cluster the GPU jobs additionally `source activate tf2-gpu`.
  Spec: `environments/ENV.yml`, `environments/tf2gpu.txt`.
* **`behav_fit`** — bambi / bauer / arviz model fitting and **the paper plotting
  notebooks**. The supplements notebook notes that bar + swarm plots only align
  correctly in `behav_fit`; `numrefields` misaligns them. The PMC posterior
  predictive check (`model.ppc(...)`) also only runs reliably here.

Install the package itself editable: `cd stress_risk && pip install --editable .`

---

## Rough edges (known, not yet fixed)

1. ~~`get_stress_level()` is out of date in git.~~ **Fixed 2026-09-01.** It now
   reads `auc_cortisol.xlsx` from inside the dataset (`addMeasures/`) instead of
   `~/Desktop/...`, takes a `bids_folder` argument, and joins the `group` column
   that `paperFinal_supplements.ipynb` expects. Verified to reproduce that
   notebook's stored output exactly.
2. **Which mask the paper numbers use is not pinned down in the committed code.**
   Decoding was run for `NPC_R`, `NPC1_R` and `NPC3_R` (compared in
   `analyse_results/decode_NPC1vs3.ipynb`), but the committed submit scripts only
   pass `--mask NPC1_R` / `NPC3_R`, while `get_decoding_info` — the function that
   builds the summary CSVs the paper reads — defaults to `mask='NPC_R'`. So the
   paper numbers are the `NPC_R` ones; the script that produced those runs isn't
   in `cluster_scripts/`. Worth adding before regenerating anything.
3. **Two BIDS roots.** Behaviour and summary CSVs live on
   `/Users/mrenke/data/ds-stressrisk`; the large decoding derivatives live on the
   external drive `/Volumes/mrenkeED/data/ds-stressrisk`. The analysis notebooks
   set both (`bids_folder` and `bids_folder_behav`).
4. ~~Absolute paths everywhere.~~ **Partly fixed 2026-09-01.** The paper-relevant
   chain now goes through `stress_risk.utils.data.BIDS_FOLDER` (one line to change)
   and the notebooks define `bids_folder` in their first cell with the department-share
   path commented above it — see [`../DATA_ON_SHARE.md`](../DATA_ON_SHARE.md).
   Figure output paths (`plot_folder_path`, `supplements_path`) are still absolute
   and point outside the repo. Exploratory code under `gradients/`, `old_scripts/`
   and `explore/` was left alone.
5. **`fit_bauerModels.py` unconditionally reads `r-prior-shift_Ediff_AUC.csv`**
   (now via `bids_folder`) even when neither `--AUC` nor `--E_dif` is passed, so
   that file must exist to refit the paper models.
6. `plots_for_paper/utils.py` is imported as a top-level `utils` module, which
   collides with `behavior/utils.py`, `analyse_results/utils.py` and
   `fmri_analysis/*/utils.py`. Whichever directory is the working directory wins.
