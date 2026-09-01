# Additional analyses — run, but not in the paper

Index of analyses that were **actually carried out and produced results**, but that
did not make it into the manuscript. Meant for reviewer questions: find the entry,
open the notebook, re-run the two or three cells.

For what *is* in the paper, see [`plots_for_paper/README.md`](plots_for_paper/README.md).

> Most of these run against `/Volumes/mrenkeED/data/ds-stressrisk` (external drive,
> decoding derivatives) and/or `/Users/mrenke/data/ds-stressrisk` (behaviour +
> summary CSVs). Notebooks under `analyse_results/` import a local `utils` module,
> so run them with that directory as the working directory.

---

## 1. Brain–behaviour link: does the neural shift track the behavioural prior shift?

**Status: done, robust correlation computed several ways, plus mediation.** This was
in the figure drafts and then cut.

**Redone on the paper's model (2026-09):**
[`plots_for_paper/brainBehav_commonPriorShift_vs_neuralShift.ipynb`](plots_for_paper/brainBehav_commonPriorShift_vs_neuralShift.ipynb)
— executed, outputs stored. Uses the **common prior shift of PMC model 5** (the
model reported in the paper) instead of the model-1 risky-prior shift, and writes
`interim_sum_data/commonPriorShift-model5_Ediff_AUC.csv`. Result:

* Common prior shift vs `E_dif`: r = +0.25, p = 0.079 (pearson, n = 49);
  robust `shepherd` r = +0.24, p = 0.11. **Not significant.**
* The old model-1 risky-prior version was r = +0.36, p = 0.011 — but the two shift
  measures correlate at r = 0.92, so this is the same construct, just attenuated.
* **Controlling for group, both vanish**: partial r = −0.15 (p = 0.31) for model 5,
  partial r = −0.03 (p = 0.85) for model 1; within-group correlations are ≈ 0
  (Control r = −0.16, Stress r = −0.17). Mediation is non-significant in both
  directions (indirect path p = 0.25). So the across-subject correlation reflects
  the **group difference in both measures**, not an individual-difference link.
  This is the honest answer to give a reviewer.
* Cortisol AUC does correlate with the common prior shift: r = +0.43, p = 0.002
  (n = 48); AUC vs `E_dif`: r = +0.25, p = 0.089.

### Original (model-1) versions

| Where | What |
| --- | --- |
| `analyse_results/shifts_decode-priors.ipynb` | The source analysis. Cells 11–14: correlation of `E_dif` (neural coding shift) with `risky_prior_mu` shift, computed with `bicor`, `shepherd` (robust, 2 outliers) and `spearman`. Cell 12 writes the combined table `interim_sum_data/r-prior-shift_Ediff_AUC.csv`. Cells 7–9: bambi model `risky_prior_mu ~ 0 + AUC*group` and `pingouin.mediation_analysis(x='group', m='AUC', y='risky_prior_mu')`. Cell 17: AUC ↔ prior shift and AUC ↔ `E_dif`. |
| `plots_for_paper/archive/paper_fig_2.ipynb` | Cells 43–47: the **figure version** — `shift-prior_E-diff_corr_robust.pdf` (shepherd correlation, r and p in the title), the same for **RNP shift** vs `E_dif`, and `pingouin.mediation_analysis` run both directions (`group → risky_prior_mu → E_dif` and `group → E_dif → risky_prior_mu`). |
| `plots_for_paper/archive/paper_fig_1.ipynb` | Cells 40–42: earlier version of the same figure. |
| `plots_for_paper/archive/poster_fig_probit.ipynb` | Cells 27–32: poster version, plus `E_dif` ↔ cortisol **AUC** correlation (`shift-{x_var}_AUC_corr_robust.pdf`). |

Data needed: `interim_sum_data/r-prior-shift_Ediff_AUC.csv`
(= per-subject prior shift + `E_dif` + AUC, written by `shifts_decode-priors.ipynb`).

The prior shift in all of the above comes from PMC **model 1**
(`subwise_change_risky_prior_model-1.csv`, written by `behavior/nlc-model1_post.ipynb`),
not the model 5 reported in the paper — which is why it was redone, see above.

Also note `build_model` defines model `9` as `risky_prior_mu ~ session*group*AUC`
(cortisol AUC on the risky prior only) — **not** a common prior shift — and it has
never been fit; there is no `model-9_trace.netcdf`. The common-prior model is `5`.

## 2. Risky/safe specificity: is the neural coding shift different for the risky vs. the safe option?

**No.** The shift in neural coding (`E_dif`) is the same size whether the risky or
the safe option was presented first, and the group effect holds equally for both.

Direct within-subject test (n = 49, computed 2026-09 from
`interim_sum_data/{within,across}_ses_decodedE.csv`, which carry `risky_first`):

* Paired t-test, risky-first vs safe-first `E_dif`: T(48) = −0.58, p = 0.567,
  d = 0.05, **BF10 = 0.18** — moderate evidence *for* the null.
  Means: risky-first +0.028, safe-first +0.037.
* Per group: Control T = −0.37, p = 0.72; Stress T = −0.44, p = 0.67.
* Mixed ANOVA (group × option): group F(1,47) = 11.09, **p = 0.002**;
  option F = 0.33, p = 0.571; interaction F = 0.01, p = 0.911.

Already-stored versions of this check:

| Where | What |
| --- | --- |
| `plots_for_paper/paperFinal_allMainPlotsStatistics_.ipynb`, *shift neural coding* section (last cell) | The group difference tested **separately per option** — safe: T = −3.13, p = 0.003, 95%CI [−0.22, −0.05]; risky: T = −3.12, p = 0.003, 95%CI [−0.21, −0.05]. Essentially identical, i.e. no risky/safe specificity. This one **is** in the paper notebook. |
| `analyse_results/shifts_decode-priors.ipynb` cell 5 | `E_dif` by group, split by `risky_first` (`col='risky_first'` catplot). |
| `analyse_results/decode_ses1-en_ses2-de_ana.ipynb` cells 7, 9 | The **across-session** `E` (not the difference) split by `risky_first`: group effect safe p = 0.004, risky p = 0.254; and the same for decodability `r` (safe p = 0.842, risky p = 0.463). Note this one *does* look asymmetric — but it is a different quantity (raw `E`, not the within/across shift) and the split halves the trials per cell. |
| `plots_for_paper/archive/paper_fig_1.ipynb` / `paper_fig_2.ipynb` | Same risky/safe split in the earlier figure drafts. |

Nothing on this lives in `fmri_analysis/encoding_model/` — the risky/safe analyses
are all downstream of decoding, in `analyse_results/` and `plots_for_paper/`.

## 3. ROI choice: NPC vs NPC1 vs NPC3

`analyse_results/decode_NPC1vs3.ipynb` — decoding was run for three parietal masks
(`NPC_R`, `NPC1_R`, `NPC3_R`), both within- and across-session. The notebook loads
all three, computes `E_diff` per ROI, and tests the group effect separately per ROI.
Answers "is the effect specific to your mask definition?".

## 4. Voxel-selection method

`analyse_results/decode_ana_01.ipynb`, cell 11 — decodability `r` compared across
voxel-selection schemes (`100` voxels, `250` voxels, and the cross-validated
`'select'` method used in the paper).

## 5. Encoding-model (nPRF) parameters between sessions and groups

| Where | What |
| --- | --- |
| `analyse_results/shifts_decode-priors.ipynb` cells 18–33 | Per-voxel nPRF `mu`, `sd`, `amplitude`, `baseline` from session 1 vs 2; group t-tests on each session difference; KS-test on whether the `mu` distribution shifts within subject; session-1/session-2 `mu` correlation per subject; amplitude as a function of `mu`. |
| `analyse_results/encoding_params.ipynb`, `encoding_params_modeling.ipynb` | Binned `mu` (in natural units) vs `amplitude`, split by session and group. |
| `analyse_results/regression_encoding_ana{,_02,_03}.ipynb` | Analysis of the **regression nPRF** variant (`fmri_analysis/encoding_model/fit_regression_encoding_model.py`), where session/group enter the encoding model directly: group comparison of `mu`, distribution checks, comparison with the standard cross-validated nPRF `cvr2`, in surface and in volume space. |

## 6. Test–retest reliability

* `behavior/explore/test-retest_reliability.py` — ICC and session-1/session-2
  correlation of `chose_risky` and of RNP.
* `plots_for_paper/archive/poster_fig_probit.ipynb` cells 22, 40 — test–retest of
  the neural `sds` (decoding uncertainty) and of `n2_evidence_sd`.

## 7. Motion / confound control

`add_measures/motion_confounds.ipynb` → `interim_sum_data/subwise_seswise_motion.csv`
(framewise displacement per subject × session). Related to decodability `r` and
`sd` in `analyse_results/decode_ana_01.ipynb` cell 16 — i.e. "is the group
difference driven by motion?".

## 8. ANS acuity ↔ risk preference; non-linear stress effects

* `behavior/add_sim&corr_NLC.ipynb` — correlation of ANS acuity (`n2_evidence_sd`)
  with `risky_prior_mu` ("in the proposed direction but not significant"), plus a
  simulation of whether a stress-induced change in perceived probability could
  produce the observed `risky_prior_mu` change.
* `analyse_results/test_Ushape.ipynb` — quadratic OLS of cortisol AUC on the
  risky-prior shift, i.e. an inverted-U dose–response test.
* `plots_for_paper/archive/poster_fig_probit.ipynb` cells 33–38 —
  `n2_evidence_sd` vs neural uncertainty (`sds`), robust correlation.

## 9. Everything-vs-everything correlation table

`analyse_results/ana_all_measures.ipynb` — puts probit RNP, decoding accuracy `r`,
decoding `sd`, cortisol AUC and self-rated stress into one table and correlates
them per group and session.

## 10. Behavioural model space beyond the reported comparison

* `behavior/utils.py::build_model` defines models `1`, `1_null`, `1a`, `2`
  (evidence-sd only), `3` (priors only), `4`, `5`, `5_noStress`, `5b`, `NLC_1`
  (with trialwise `n_hat` saved), `EU_1`–`EU_3`, `EU_noStress`. Only `5`, `5_noStress`,
  `EU_3`, `EU_noStress` are in the supplements comparison.
* `behavior/nlc-model_comp.ipynb`, `fit_bauer_add.ipynb` — the broader comparisons.
* `behavior/nlc-model5_diffObjPrior.ipynb` — model 5 with different objective priors.
* `behavior/sim_NLC_sesgrEffects.ipynb` — simulation of what session/group effects
  the model can in principle recover.
* `behavior/eu_model_posterior.ipynb`, `probit-model_fit&postPlot.ipynb`,
  `probit-model_poster-pred.ipynb` — full posterior/PPC exploration of the EU and
  probit models, including which subjects are risk-*seeking* by RNP.
* `fit_bauerModels.py --AUC` / `--E_dif` fit PMC variants with cortisol AUC or the
  neural shift as a subject-level regressor; analysed in
  `behavior/analyze_bauer_model.py` / `analyze_bauer_model2.py`.

## 11. Value / EV representations (mPFC)

* `fmri_analysis/mPFC_value_decoding/value_event_files.ipynb` — builds event files
  with trialwise `Vhat` from the PMC model's `n1_hat`/`n2_hat`
  (`model-NLC_1_trace.netcdf`).
* `fmri_analysis/glm_scripts/` + `glm_classic/` — SPM first/second level for `EV`,
  `EU`, `Vhat`, `Vchoice` models; `vis_SPM_nilearn.ipynb` does cluster-level
  inference, mPFC-masked correction and the cluster tables
  (`interim_sum_data/glm_table_{model}_{contrast}.csv`).
* `analyse_results/value-decoding.ipynb` — decoding run on the value-GLM betas
  (`--value` flag through the encoding/decoding scripts).
* `fmri_analysis/surface/create_mPFCmask.py`, `vmPFC_try.ipynb` — mPFC mask
  construction.

## 12. Anatomical / specificity controls

* `analyse_results/amplitude_visualCortex.ipynb` — Benson/neuropythy retinotopic
  atlas → V1 mask; nPRF amplitude in visual cortex as a control region.
* `fmri_analysis/lateralization/` — L vs R differences in `r2` and `mu` maps
  (`r2maps_dif.ipynb`, `vis_mu-r2maps_.ipynb`, `vis_r2_maps.py`).

## 13. Functional gradients

`fmri_analysis/gradients/` — a substantial side project (connectivity gradients of
the risk task, alignment via Procrustes and FUGW, morphospace comparisons,
relation of gradients to nPRF `r2`). Its own overview is in
`fmri_analysis/gradients/analsyis_summary.md`; the current fitting script is
`fit_grad_procrust.py`.

## 14. Raw behaviour / task-design figure

`plots_for_paper/archive/fig1_rawData.ipynb` → `order_range_rawData.png`, and
`behavior/plot_rawData.ipynb`. Choice behaviour by presentation order and
numerosity range.

## 15. Physiology beyond the reported HRV

`add_measures/physio_hrv_ANS.ipynb` — method development for HRV and additionally
**EDA / SCR** (skin conductance) features, plus frequency-domain analysis.
`physio_hrv_loops.ipynb` cells 16+ correlate HRV measures with the prior shift and
the neural shift.
