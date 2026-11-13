# Archived paper-figure notebooks

These are **superseded drafts**. Everything that made it into the paper is now in
the two `paperFinal_*` notebooks one level up — see [`../README.md`](../README.md).

Nothing here is deleted because several of these notebooks contain analyses that
were *run and completed* but then cut from the manuscript. If a reviewer asks for
something extra, look here first — the index of those analyses is in
[`../../ADDITIONAL_ANALYSES.md`](../../ADDITIONAL_ANALYSES.md).

## Caveat when re-running

`paper_fig_1.ipynb`, `paper_fig_2.ipynb` and `poster_fig_probit.ipynb` do
`from utils import ...`, expecting `plots_for_paper/utils.py` to be next to them.
After the move you need to run them with `plots_for_paper/` on the path, e.g.:

```python
import sys; sys.path.insert(0, '..')
```

## What each one was

| Notebook | Last touched | What it was |
| --- | --- | --- |
| `paper_fig_2.ipynb` | 2024-09 | **Closest predecessor of the final main notebook.** Probit + PMC + decoding + the brain–behaviour correlations. Superseded by `paperFinal_allMainPlotsStatistics_`, except that the brain–behaviour section was dropped rather than moved. |
| `paper_fig_1.ipynb` | 2024-03 | Earlier full-figure draft. Same structure as `paper_fig_2` plus PMC baseline estimates and the cortisol AUC group difference (the latter now lives in the supplements notebook). |
| `paper_fig_2_nlc-b.ipynb` | 2024-09 | Variant analyses: probit **indifference point** instead of RNP ("more risk neutral?"), and the first use of PMC model-label `5` (priors shift together) that became the paper model. |
| `poster_fig_probit.ipynb` | 2023-10 | SfN/lab-poster version. Contains several correlation analyses not in any paper draft (see the additional-analyses index). |
| `fig1_rawData.ipynb` | 2023-12 | Raw behaviour / task design figure (`order_range_rawData.png`). Not in the paper. |
| `fig2_rnp.ipynb` | 2023-12 | Standalone probit/RNP figure set, incl. per-group posterior plots. |
| `fig3_NLC.ipynb` | 2023-10 | PMC ("NLC") figures for the earlier **model 6** and **model 1** specifications, before the switch to model 5. |
| `fig4_decoding.ipynb` | 2023-09 | First `E_diff` group figure. |
| `fig5_glm.ipynb` | 2023-09 | GLM figure draft (no saved outputs). |
| `fig6_across-data-modalities.ipynb` | 2023-09 | Attempt at a combined behaviour/neural/physiology figure (no saved outputs). |
| `addfig3_decode.ipynb` | 2023-08 | Small decoding bar-plot add-on. |
| `likelihood_prior.ipynb` | 2023-10 | Bayesian-inference schematic development; the final version of this code was extracted into `../utils.py`. Writes to `/data/ds-risk/...` — inherited from the *risk_experiment* project, not this dataset. |
| `gilles_NLC-figure2.ipynb` | 2023-09 | **From the other project.** Gilles' 3T/7T NLC figures on `ds-risk`; kept as a style/structure reference only. Does not run on the StressRisk dataset. |
