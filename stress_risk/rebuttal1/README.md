# Reviewer response, round 1 (Nature Communications, 2026)

Analyses run for the first revision. `R1.1` = reviewer 1, point 1; the labels match the
docstrings of the scripts. Each script's docstring explains the question, the method and
how to run it; this file is only the index.

The work is spread over three folders:

| Folder | What is in it |
| --- | --- |
| `stress_risk/rebuttal1/` (here) | The analysis scripts. |
| [`../../rebuttal_figures/`](../../rebuttal_figures/) | Self-contained scripts that write their output next to themselves: the corrected Supplementary Table 1 and the design-power figure. |
| [`../../notes/rebuttal1/`](../../notes/rebuttal1/) | `proposed_manuscript_edits.md` (the text changes to the paper) and `results/` (every figure and CSV the scripts here write). |

Not in git, because this repo is public: the reviewer reports, the manuscript draft, the
response letter and the script that builds it, and participant-level tables. They are in
`notes/rebuttal1/private/` on Gilles's machine (see `.gitignore`).

## Scripts

All scripts load the PMC traces through `common.py`, which documents the design-matrix
coding (session is 1/2, not 0/1; see the Supplementary Table 1 correction).

| Script | Point | Question | Writes to `notes/rebuttal1/results/` |
| --- | --- | --- | --- |
| `common.py` | — | Shared loaders: behaviour, per-cell PMC parameters, decoded posteriors | — |
| `step2_perceived_ev.py` | R1.1 | How can a prior shift shared by both options increase risk-seeking? Perceived EV vs objective EV | (curves used by `fig4_mechanism.py`) |
| `fig4_mechanism.py` | R1.1 | New Figure 4: fitted priors and noise against the payoffs shown, and the perceived-value curves they imply | `fig4_mechanism.{pdf,png}`, `fig4_mechanism_parameter_values.csv` |
| `step8_equal_width_counterfactual.py` | R1.1 | Is the prior-width asymmetry *necessary* for the effect? Counterfactual with equal or swapped widths | `equal_width_counterfactual.csv` |
| `step3to5_neural.py` | R1.2 | Risky vs safe options in the decoded parietal signal, on numerosity-matched trials | (trial table, not in git) |
| `step6_baseline.py` | R1.3 | Do the groups differ at session 1 on any PMC parameter? | `rebuttal_baseline_contrasts.csv` |
| `step11_baseline_choice.py` | R1.3 | Same question, model-free: raw P(chose risky) at session 1 | `fig_baseline_choice`, `fig_group_session_choice` |
| `step7_physiology.py`, `step7_physiology_bayes.py` | R2.2 | Do cortisol, self-rated stress or HRV predict the prior or neural shift? (frequentist, then per posterior draw) | `rebuttal_physiology_{correlations,bayesian}.csv` |
| `step9_amylase.py` | R2.2 | Salivary alpha-amylase, the second marker in the assay file | `fig_saliva_markers`, `rebuttal_amylase_correlations.csv` |
| `step10_saliva_auc.py` | R2.2 | AUC of the saliva curves on real elapsed time rather than sample position | `fig_saliva_auc`, `rebuttal_saliva_auc_{contrasts,correlations}.csv` |
| `make_figures.py` | R1.2, R1.3, R2.2 | Figures from the outputs above | `fig_baseline_contrasts`, `fig_neural_riskysafe`, `fig_correlations`, `fig_choice_proportions`, `fig_group_parameters`, `fig_prior_vs_objective`, `fig_psychometric` |

Elsewhere in the repo:

| Location | Point | Question |
| --- | --- | --- |
| [`../analyse_results/probit_order_interaction.ipynb`](../analyse_results/probit_order_interaction.ipynb) (fits in `fit_probit_order.py`) | — | Does the stress effect depend on presentation order? Writes `fig_probit_order_*` |
| [`../power_analysis/plot_design_power.py`](../power_analysis/plot_design_power.py) | R2.3 | Why the group × session design: power of the 2022 candidate designs |
| [`../../rebuttal_figures/power_within_vs_between.py`](../../rebuttal_figures/power_within_vs_between.py) | R2.3 | Power of the design that was run vs a single-session between-group design |
| [`../../rebuttal_figures/supp_table1.py`](../../rebuttal_figures/supp_table1.py) | R1.3 | Corrected Supplementary Table 1, with checks |

Results and interpretation of entries 16–19 are written up in
[`../ADDITIONAL_ANALYSES.md`](../ADDITIONAL_ANALYSES.md); the text changes they lead to are
in [`../../notes/rebuttal1/proposed_manuscript_edits.md`](../../notes/rebuttal1/proposed_manuscript_edits.md).
