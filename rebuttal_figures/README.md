# Reviewer-response scripts with their outputs

Self-contained scripts for the first revision. Each writes its output next to itself and
says in its docstring how to run it. The other reviewer-response analyses are indexed in
[`../stress_risk/rebuttal1/README.md`](../stress_risk/rebuttal1/README.md).

| Script | Outputs | What it is |
| --- | --- | --- |
| `supp_table1.py` | `supp_table1.{md,csv}`, `supp_table1_diff.{md,csv}`, `supp_table1_checks.md` | **Corrected Supplementary Table 1.** The published per-cell PMC values were computed with session coded 0/1; the model was fitted with 1/2. `supp_table1.md` is ready to paste into the manuscript. The checks confirm the coding from the stored design matrices, reproduce the old table, and reproduce every main-text effect. |
| `power_within_vs_between.py` | `power_within_vs_between.{pdf,png}`, `power_within_vs_between_summary.txt` | Power of the group × session design vs a single-session between-group design, from the control group's test–retest reliability. |
