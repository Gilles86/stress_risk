# Proposed manuscript edits arising from the reviews

Three edits. The first two are corrections we found while answering Reviewer 1;
the third is the new material R1's first point asks for.

---

## 1. Methods — group assignment (CORRECTION)

**Where:** Methods, participants/design section, the sentence currently reading
that subjects were *"randomly assigned to the stress group"*.

**Why:** allocation was balanced, not simple randomisation. The balance check
performed at the time of allocation (MATLAB figure, `image (1).png`) tested two
session-1 measures — decodability of payoff magnitude from parietal cortex, and
risk aversion (risk-neutral probability) — reporting p = 0.839 and p = 0.806
respectively, with 51% of participants allocated to treatment. The assignment
record `StressRiskNum_ConditionAssigned.csv` carries the resulting `rank_decode`
stratum and `condition`; within each stratum the two conditions are balanced
(17/17, 7/7, 3/3, 2/1).

**Replacement text:**

> Participants completed the first session before any manipulation. They were
> then allocated to the stress or the control group so as to balance two
> measures obtained in that session: the decodability of payoff magnitude from
> parietal cortex, and risk aversion as indexed by the risk-neutral probability.
> Balance was confirmed on both (decodability p = 0.84; risk aversion p = 0.81),
> with 51% of participants allocated to the stress condition. Choice consistency
> was not used as an allocation criterion and did not differ between the groups
> at baseline (2.11 vs 2.18, BF10 = 0.31).

## 2. Supplementary Table S1 — per-cell parameter values (CORRECTION)

**Where:** Supplementary Table S1, and the Methods sentence describing the
regression dummies.

**Why:** the table's per-cell values were computed by evaluating the regression
with `session` coded 0 and 1, but the model was fitted with `session` coded 1
and 2. This is verifiable directly from the design matrix stored in the fitted
model (`constant_data/_dm_*` in `model-5_trace.netcdf`), whose four unique rows
are `[1, s, g, s*g]` with `s` in {1, 2}. Every cell in the published table is
displaced by one session step: the "session 1" column is the model's
extrapolation to a session 0, and the "session 2" column holds the session-1
estimates.

**Scope:** regression coefficients are unaffected, and therefore so is every
effect reported in the main text — session effects, the group x session
interaction, and all differences between cells are invariant to the shift. Only
the absolute per-cell values change, and the baseline group contrast that can be
read from them (published table implies -0.52; the model's estimate is -0.013,
95% CrI [-0.415, +0.389]).

**Action:** replace Table S1 with the corrected values
(`rebuttal_figures/supp_table1.md`, made by `rebuttal_figures/supp_table1.py`), and correct the Methods
sentence stating that the dummies take values 0 or 1.

---

## 3. Results — mechanism paragraph + new Figure 4 (NEW MATERIAL)

**Where:** Results, section *"Acute stress leads to more optimistic beliefs
about magnitudes"*, as a new paragraph at the end of the section, after the
group x session interaction on the prior mean is reported.

**New paragraph:**

> How can a shift in a prior that is common to both options make participants
> more risk-seeking? The answer lies in the different precisions of the two
> priors. A percept is a precision-weighted compromise between evidence and
> prior, and the weight given to the evidence, w = sigma^2 / (sigma^2 + nu^2),
> is close to one when the prior is wide and falls as the prior becomes more
> precise. Because the prior over safe payoffs is approximately twice as wide as
> the prior over risky payoffs (Figure 4B, Table S1), the safe percept is governed almost
> entirely by the presented magnitude, whereas the risky percept is drawn
> substantially towards the prior. An upward shift in a prior mean shared by
> both options therefore raises the perceived value of the risky option
> considerably more than that of the safe option, and shifts choices towards the
> risky option (Figure 4D). This asymmetry is not incidental but a precondition
> for the effect: were the two priors equally precise, a common prior mean would
> cancel from the decision variable once averaged over the counterbalanced
> presentation order, and could not change risk attitude at all.

**New Figure 4**, from `notes/rebuttal1/results/fig4_mechanism.pdf`
(`stress_risk/rebuttal1/fig4_mechanism.py`, model 5; the parameter values behind it
are in `fig4_mechanism_parameter_values.csv`). Existing Figure 4 and later become
Figure 5 onwards.

**Legend:**

> **Figure 4. How a shared shift in the prior mean produces risk-seeking.**
> **A-C.** Group-level parameters of the cognitive model, posterior means with 95%
> credible intervals; open markers, session 1; filled markers, session 2.
> **A.** Prior mean per option, in payoff units. Grey band, geometric mean +/-1 SD of
> the payoffs actually shown for that option; dashed line, their mean. **B.** Prior
> width sigma, in log units; dashed line, the SD of the log payoffs shown, the value
> a calibrated prior would take. The prior over safe payoffs is about twice as wide
> as the prior over risky payoffs in every cell. **C.** Evidence noise nu for the
> first- and second-presented option; nu has no objective reference, being a property
> of the observer rather than of the stimulus set. **D.** Perceived expected value
> against objective expected value for the risky (red) and safe (blue) option, shown
> separately for each presentation order and group. Dashed lines, session 1; solid
> lines, session 2; shaded areas, 95% credible intervals; grey dashed line, veridical.
> Only in the stress group does the perceived value of the risky option rise from the
> first to the second session; the safe percept is almost unchanged, because the wider
> safe prior leaves it dominated by the presented magnitude.

**Note on calibration.** Panels A and B also show that neither prior becomes better
calibrated under stress: the risky prior is too narrow (sigma about 0.37 against an
objective 0.60) and the safe prior too wide (0.60-0.88 against 0.49) in every cell,
and the safe prior mean moves further from the payoffs shown in session 2 of the
stress group (P(closer) = 0.05). The Discussion's "more veridical prior" wording
does not hold under the reported model and needs revising — see the note under
*Not yet resolved*.

**Also for R1's minor points d and e**: relabel the existing Figure 3A rows as
"value (log space)" and "expected value (natural space)". (The counterfactual
variant sketched earlier -- optimistic versus pessimistic prior -- was dropped.)

---

## Not yet resolved

- Discussion wording: "priors become more aligned with the objective payout
  distribution". Not supported by model 5 (see the calibration note in section 3);
  it does hold under model 1, the parameterisation where the two prior means move
  separately, which is not the model the paper reports.
- Whether the two decoders entering the shift-in-neural-coding measure use
  matched voxel sets (within-session filenames carry no voxel count, across-session
  ones carry `nvoxels-NN`). Bears on the absolute interpretation of that measure,
  not on the group comparison.
