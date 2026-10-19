"""R2.2: do the stress measures predict the behavioural and neural effects?

Reviewer 2 asks which component of the stress response drives the mechanism. The
study was not designed to detect individual differences (25 per group), so every
correlation is reported with a Bayes factor and an explicitly exploratory framing.

Predictors : cortisol AUC, self-rated stress, HRV (SDNN, RMSSD, LF/HF, mean HR)
Outcomes   : common prior shift (PMC model 5), shift in neural coding (E_dif)

Uses the CSVs only - auc_cortisol.xlsx needs openpyxl, and the AUC values are
already carried in commonPriorShift-model5_Ediff_AUC.csv.
"""
import os.path as op

import numpy as np
import pandas as pd
import pingouin as pg

BF = '/Users/gdehol/data/ds-stressrisk'
OUT = '/Users/gdehol/git/stress_risk/notes/rebuttal1/results'


def load():
    p = op.join(BF, 'interim_sum_data')
    d = pd.read_csv(op.join(p, 'commonPriorShift-model5_Ediff_AUC.csv'))
    stress = pd.read_csv(op.join(BF, 'addMeasures', 'selfRated_Stress.csv'))
    d = d.merge(stress[['subject', 'mean_stress']], on='subject', how='left')

    hrv = pd.read_csv(op.join(p, 'HRV_var-v1_sampRate-500_subwise.csv'))
    # session-2 minus session-1, averaged over runs: the change under the manipulation
    agg = (hrv.groupby(['subject', 'session'])[['HRV_SDNN', 'HRV_RMSSD',
                                                'HRV_LFHF', 'HR_bpm']].mean())
    ch = (agg.xs(2, level='session') - agg.xs(1, level='session')).add_suffix('_change')
    return d.merge(ch.reset_index(), on='subject', how='left')


def table(d, outcomes, predictors, label, covar='group'):
    """Zero-order and group-corrected (partial) correlations side by side.

    The raw across-subject correlation is not interpretable here: the stress group
    has both a higher cortisol AUC and a larger prior shift BY CONSTRUCTION, so any
    such correlation partly re-expresses the group effect. The partial correlation
    controlling for group is the individual-difference question that was asked.
    """
    rows = []
    for o in outcomes:
        for x in predictors:
            s = d[[o, x] + ([covar] if covar else [])].dropna()
            if len(s) < 8:
                continue
            r = pg.corr(s[x], s[o], method='pearson')
            rec = dict(outcome=o, predictor=x, n=len(s),
                       r_raw=r['r'].iloc[0], p_raw=r['p-val'].iloc[0],
                       BF10_raw=float(r['BF10'].iloc[0]))
            if covar and s[covar].nunique() > 1:
                pr = pg.partial_corr(s, x=x, y=o, covar=covar)
                rp = pr['r'].iloc[0]
                rec.update(r_partial=rp, p_partial=pr['p-val'].iloc[0],
                           # one covariate costs one df, so score the BF at n-1
                           BF10_partial=float(pg.bayesfactor_pearson(rp, len(s) - 1)))
            rows.append(rec)
    t = pd.DataFrame(rows)
    key = 'BF10_partial' if 'BF10_partial' in t else 'BF10_raw'
    t['evidence'] = np.where(t[key] > 3, 'for effect',
                     np.where(t[key] < 1 / 3, 'for null', 'inconclusive'))
    print(f"\n=== {label} ===")
    print(t.round(3).to_string(index=False))
    return t


def main():
    d = load()
    outcomes = ['prior_shift', 'E_dif']
    predictors = ['AUC', 'mean_stress', 'HRV_SDNN_change', 'HRV_RMSSD_change',
                  'HRV_LFHF_change', 'HR_bpm_change']
    print(f"subjects: {len(d)}  (stress {int((d.group == 1).sum())}, "
          f"control {int((d.group == 0).sum())})")

    all_t = table(d, outcomes, predictors,
                  'All subjects - raw vs corrected for group')
    str_t = table(d[d.group == 1], outcomes, predictors,
                  'Stress group only (group is constant, so raw = the analysis)',
                  covar=None)

    print("\n=== The two effects against each other ===")
    for tag, dd in [('all', d), ('stress only', d[d.group == 1]),
                    ('control only', d[d.group == 0])]:
        s = dd[['prior_shift', 'E_dif']].dropna()
        r = pg.corr(s.prior_shift, s.E_dif)
        print(f"  {tag:13s} n={len(s):2d}  r={r['r'].iloc[0]:+.3f}  "
              f"p={r['p-val'].iloc[0]:.3f}  BF10={float(r['BF10'].iloc[0]):.2f}")
    s = d[['prior_shift', 'E_dif', 'group']].dropna()
    pr = pg.partial_corr(s, x='prior_shift', y='E_dif', covar='group')
    print(f"  controlling for group   r={pr['r'].iloc[0]:+.3f}  p={pr['p-val'].iloc[0]:.3f}")

    out = pd.concat([all_t.assign(sample='all'), str_t.assign(sample='stress')])
    out.to_csv(op.join(OUT, 'rebuttal_physiology_correlations.csv'), index=False)
    print(f"\nsaved {OUT}/rebuttal_physiology_correlations.csv")


if __name__ == '__main__':
    main()
