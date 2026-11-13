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

## 16. Salivary alpha-amylase — the second marker in the assay file

**Status: done 2026-09-22 (reviewer-response round 1).** Gökhan pointed out that the
saliva assay also measured **alpha-amylase**, a fast autonomic marker (immediate
onset, back to baseline in 15–20 min) as against cortisol's slow glucocorticoid
response, and that participants were re-stressed three times during the experiment.

`rebuttal1/step9_amylase.py` — run with `~/mambaforge/envs/risk7t/bin/python` (needs
openpyxl + pingouin + arviz together). Both markers are in
`addMeasures/auc_cortisol.xlsx` despite the name: `Cortisol_1/_2` and
`Amylase_1/_2` are duplicate assay runs (r = 0.98), `TimePoint` is the sample's
position within participant, 1–6. Sample timing is mapped to the Methods there;
samples 2–6 are `onset_Saliva_1..5` in `addMeasures/data_combined.xlsx`, sample 1
(arrival) is not logged.

* **Cortisol replicates the paper**: stress > control at the two during-MIST samples
  (p = 0.004 both), AUC t = +5.31, BF10 ≈ 4900.
* **Amylase shows no reactivity difference**: group × sample interaction
  F = 0.45, p = 0.82 (F = 0.62, p = 0.69 on log amylase); during-MIST rise over the
  pre-MIST sample −11.0 vs +0.5, p = 0.66, BF10 = 0.33. The groups differ in
  *level* (group main effect p = 0.034), driven by the control group's decline after
  arrival, not by a stress-evoked rise. Both groups rise at +65 min (post-scan /
  debriefing).
* **No association with the behavioural effect.** Group-controlled partial
  correlation with the participant-level prior shift, per posterior draw: amylase
  AUC r = −0.00 [−0.26, +0.26], during-MIST rise r = +0.08 [−0.28, +0.37], peak rise
  r = −0.00 [−0.30, +0.28]. Cortisol AUC reproduces step 7 exactly (r = −0.090
  [−0.343, +0.163]), which cross-validates the pipeline.
* Cortisol AUC and the amylase rise are essentially independent (r = +0.03, n = 40).

Outputs: `notes/rebuttal1/results/fig_saliva_markers.{pdf,png}` (both markers over
the six samples by group, with per-sample significance markers),
`rebuttal_amylase_correlations.csv`, `rebuttal_amylase_subjectwise.csv`.

**Manuscript issue found:** the Methods say "A total of seven saliva samples were
collected" and then enumerate six (−40, 0, ~20, ~37, 51, 65 min); the data has six.
Also, the nominal minutes are the intended protocol — the logged medians are
0, +33, +55, +70, +79.

## 17. AUC of the saliva curves, on real elapsed time

**Status: done 2026-09-22 (reviewer-response round 1).**
`rebuttal1/step10_saliva_auc.py` (same env as entry 16).

**What the paper's cortisol AUC actually is.** Reverse-engineered from the shipped
`AUC` column: the trapezoid of (cortisol − `estCircadianChange`) over samples 2–6,
integrated against the **sample index**, not minutes (reproduced to r = 0.998).
`add_measures/saliva_analysis.py` shows the index integration. The circadian
correction is sound; the equal spacing is not — the logged gaps are 40, 33, 22, 15
and 8 minutes.

* **The cortisol conclusion is robust to this.** Recomputed against each
  participant's own logged sample times, the two measures correlate at r = 0.986 and
  the group contrast barely moves: t = +4.36, p < 0.001, BF10 = 268, d = 1.31
  (index version t = +4.61, BF10 = 530, d = 1.39; n = 22/23 complete curves).
* Raw (uncorrected) Pruessner AUCs, same window: AUCg t = +3.11, p = 0.004,
  BF10 = 11.8; AUCi t = +2.26, p = 0.029, BF10 = 2.2. So most of the strength of the
  reported effect comes from the circadian correction, not from the AUC per se —
  worth knowing if a reviewer asks for the raw version.
* **Amylase, on real time, tells the same story as entry 16**: AUCg differs by group
  (t = +2.32, p = 0.028, BF10 = 2.4) but AUCi — the reactivity measure — does not
  (t = −0.37, p = 0.71, BF10 = 0.33). A level difference, not a response difference.
* **No AUC predicts the prior shift** once group is controlled: every 95% CrI spans
  zero (cortisol AUCcc minutes r = −0.10 [−0.35, +0.17]; amylase AUCi r = +0.09
  [−0.29, +0.39]).

Outputs: `notes/rebuttal1/results/fig_saliva_auc.{pdf,png}`,
`rebuttal_saliva_auc_{contrasts,correlations,subjectwise}.csv`.

## 18. Does the stress effect on risky choice depend on presentation order?

**Status: done 2026-09-28 (reviewer-response round 1). No, it does not.**
[`analyse_results/probit_order_interaction.ipynb`](analyse_results/probit_order_interaction.ipynb)
(executed, outputs stored). The fits are in `analyse_results/fit_probit_order.py`, which writes
`derivatives/cogmodels/bambi-RNP-fit_trace_model-{paper,order,order_re}.netcdf`. Run in
`risk7t` (bambi 0.15.0, pymc 5.25.1) because there is no `behav_fit` env on that machine.
Priors are bambi's defaults and sampler settings are the paper's. None of the three fits has
divergences, and r_hat ≤ 1.01 throughout.

The paper's probit model with order (`order`, 1 = risky first) crossed with everything:
`chose_risky ~ x*session*group*order + (x*session|subject)`, where x = log(risky/safe).
The stress effect is the group × session difference-in-difference in RNP, as in Figure 2B.

* **Refit check:** the paper model refit in the current bambi reproduces the stored
  `bambi-RNP-fit_trace_model1` (bambi 0.9.2): RNP interaction 0.066 [−0.004, 0.137],
  p_bayes = 0.031, against 0.066 [−0.005, 0.142], p_bayes = 0.034 stored (paper: 0.07
  [−0.01, 0.14], 0.034). The bambi version change does not matter.
* **Stress effect on RNP per order:** safe first +0.069 [0.003, 0.140], p_bayes = 0.021;
  risky first +0.061 [−0.017, 0.144], p_bayes = 0.064. Both are the same size as the pooled
  effect (0.066). The risky-first interval is slightly wider and just touches 0.
* **Slope (choice consistency) stress effect per order:** safe first −0.17 [−0.68, 0.34];
  risky first +0.08 [−0.44, 0.61]. Neither differs from zero, as in the paper.
* **Group × session × order:** the difference in the RNP stress effect between orders
  (risky − safe) is −0.008 [−0.060, 0.043], p_bayes = 0.38. Coefficients:
  `session:group:order` −0.24 [−0.70, 0.22] (intercept) and `x:session:group:order`
  +0.25 [−0.34, 0.85] (slope). These partly offset each other, which is why the RNP
  difference is ≈ 0.
* **Raw check, no model:** the stress − control DiD in P(risky) is +0.091 for safe first
  and +0.076 for risky first.
* **Sensitivity:** order varies within subject, so a second model adds by-subject order
  slopes (`order_re`: `(x*session*order|subject)`). It gives the same answer: per order
  +0.070 [0.004, 0.141] and +0.060 [−0.021, 0.146]; difference −0.009 [−0.061, 0.044].

**Limitation for the figure.** `notes/rebuttal1/results/fig_probit_order_ppc.{pdf,png}`
uses the Figure 3B layout (stake × order × group × session). It shows that the probit has
**no stake term**, so its predictions are flat over stake and miss the strong stake × order
pattern: with risky first, P(risky) falls from ≈0.67 at stake 7 to 0.27–0.40 at stake 28. That pattern is what
the PMC model is for. The probit answers "does the stake-averaged stress shift differ by
order". Whether stress changes the stake × order *pattern* is a PMC question (Figure 3B).
Also `fig_probit_order_stress_effect.{pdf,png}`: the posterior RNP stress effect per order
next to the paper model's.

Side note: the Methods give the random effects as `((1 + log_risky_safe)|subject)` and
"4 chains of 2000 samples each (1000 burnin)". The trace that was actually used has
`(x*session|subject)` and 1000 tune + 1000 draws per chain.

## 19. Model-free baseline: did the groups already differ in risky choice at session 1?

`rebuttal1/step11_baseline_choice.py` (run with
`PYTHONPATH=<repo> ~/mambaforge/envs/tms_risk/bin/python`; needs pingouin + statsmodels).
Complements entry R1.3 / `step6_baseline.py`, which contrasts the PMC parameters.

* **Yes, a small one.** Session-1 P(chose risky): control 0.514, stress 0.449;
  Δ = −0.065, 95% CI [−0.120, −0.010], t(48) = −2.38, p = 0.021, d = 0.67, BF10 = 2.69.
  Welch, Mann–Whitney and a 20k permutation test all give p ≈ 0.02. At session 2 the
  groups do not differ (t = 0.32, p = 0.75, BF10 = 0.30).
* **Neither RNP nor slope differs significantly on its own.** In the paper probit model
  the session-1 slope (choice consistency) is lower in the stress group but not credibly
  so: −0.26 [−0.75, +0.23], P(>0) = 0.14; unpooled per-subject probit fits t(48) = −1.05,
  p = 0.30, Mann–Whitney p = 0.32. The gap is the same at session 2 (−0.31 [−0.93, +0.31]) and
  stress does not change it (group × session −0.05 [−0.47, +0.37]), so it looks like a
  stable group difference in consistency. A simple trial-level logit with
  subject-clustered SEs gives group × log-ratio −1.12, p = 0.020, but it has no
  random slopes and overstates the evidence; use the probit numbers. The raw-proportion
  gap (p = 0.02) is the sum of two small, non-significant differences (RNP −0.02, slope
  −0.26) that both push the same way. For comparison, the PMC's only near-credible
  baseline contrast is `n1_evidence_sd` (stress noisier, P(>0) ≈ 0.89–0.93); the prior
  mean is −0.013 [−0.41, +0.39].
* **Don't t-test this model's per-subject estimates.** `group` is a fixed effect, so
  each subject is shrunk toward its own group's mean; within-group spread shrinks and a
  t-test on posterior medians is anti-conservative (it gave slope p = 0.08 against
  p = 0.30 for unpooled fits). Use the population-level contrast, or unpooled fits.
* The apparent baseline prior gap of −0.52 in the published Table S1 was the
  session-0/1-vs-1/2 coding error (see proposed edits §2); the raw-choice gap here is
  real and independent of that.

* **Against the stress effect.** Raw P(risky) change: control +0.024, stress +0.107;
  DiD +0.083, t(48) = 1.54, p = 0.13, BF10 = 0.74; ANCOVA (ses-2 ~ group + ses-1)
  +0.064, p = 0.26. With test–retest r = 0.31, regression to the mean alone predicts a
  DiD of +0.045 from the baseline gap — about half the raw effect. The paper's effect is
  on RNP (0.07, p_bayes = 0.034), which separates curve position from slope; the
  baseline gap is in slope, the session-2 change is a leftward shift (see right panel).
* **No baseline difference in risk attitude (RNP).** Paper probit model
  (`bambi-RNP-fit_trace_model-paper`, RNP = exp(a/b)): session-1 stress − control
  −0.018 [−0.145, +0.113] at the population level; unpooled per-subject probit fits
  t(48) = 0.74, p = 0.46, Mann–Whitney p = 0.94. The same trace reproduces the paper's
  group × session effect, +0.066 [−0.004, +0.137], p_bayes = 0.031. So the baseline
  gap in raw choice proportions is not a gap in the quantity the paper reports.

Outputs: `notes/rebuttal1/results/fig_baseline_choice.{pdf,png}`,
`fig_group_session_choice.{pdf,png}` (paired per-subject P(risky) and RNP by group ×
session, with all tests; choice curves for all four cells — the one-figure summary).

## 20. Supplementary Table 1 — correction (changes paper numbers)

**Status: done 2026-10-19 (reviewer-response round 1). This is a correction, not an
additional analysis.** [`rebuttal_figures/supp_table1.py`](../rebuttal_figures/supp_table1.py)
regenerates the table; outputs and checks are next to it.

* The published per-cell PMC values (`plots_for_paper/paperFinal_supplements.ipynb`, cell 3)
  evaluated the regression with session coded 0/1. The model was fitted with 1/2 (the design
  matrices stored in `model-5_trace.netcdf` say so), so every cell was one session step too
  early. Regression coefficients, and so every main-text effect, are unchanged.
* With the correct coding no parameter differs between the groups at session 1. The prior
  mean gap is −0.013 [−0.415, +0.389], not the −0.52 the published table implied.
* The script reproduces the old table exactly with 0/1 coding, and all seven main-text PMC
  effects and Supplementary Table 2 with either coding. See `supp_table1_checks.md`.
