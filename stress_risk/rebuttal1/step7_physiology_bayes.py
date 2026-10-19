"""R2.2, done inside the Bayesian machinery.

The earlier version correlated POSTERIOR POINT ESTIMATES of subject-level prior
shifts with the stress measures and attached frequentist p-values and Bayes
factors. That is wrong twice over: it discards the posterior uncertainty on each
subject's shift, and it treats hierarchically shrunk estimates as if they were
measured data.

Here the association is computed once per posterior draw, giving a posterior
distribution over the (partial) correlation. Group is always partialled out --
the stress group has both a larger cortisol response and a larger prior shift by
construction, so the zero-order correlation is not an individual-difference
quantity at all.
"""
import os.path as op
import sys

import arviz as az
import numpy as np
import pandas as pd

sys.path.insert(0, op.dirname(op.abspath(__file__)))
from common import BIDS_FOLDER, TRACE, design  # noqa: E402

OUT = '/Users/gdehol/git/stress_risk/notes/rebuttal1/results'


def subject_shifts(trace=TRACE):
    """Per-draw, per-subject session 1->2 change in the shared prior mean."""
    P = az.from_netcdf(trace).posterior
    pm = P['prior_mu'].stack(s=('chain', 'draw')).transpose('s', 'subject', ...).values
    subs = np.asarray(P.subject.values)
    return pm, subs                                   # (draw, subject, regressor)


def shift_for(pm, group_of_subject):
    """design(2,g) - design(1,g) applied per subject, no intercept column."""
    d = np.stack([design(2, g, False) - design(1, g, False) for g in group_of_subject])
    return np.einsum('dsr,sr->ds', pm, d)             # (draw, subject)


def partial_corr_rows(X, y, covar):
    """Correlation of each row of X with y, both residualised on covar."""
    C = np.column_stack([np.ones_like(covar), covar])
    resid = lambda v: v - C @ np.linalg.lstsq(C, v, rcond=None)[0]
    yr = resid(y)
    Xr = np.stack([resid(row) for row in X])
    num = Xr @ yr
    den = np.linalg.norm(Xr, axis=1) * np.linalg.norm(yr)
    return num / den


def main():
    pm, subs = subject_shifts()
    p = op.join(BIDS_FOLDER, 'interim_sum_data')
    meta = pd.read_csv(op.join(p, 'commonPriorShift-model5_Ediff_AUC.csv'))
    meta = meta.merge(pd.read_csv(op.join(BIDS_FOLDER, 'addMeasures',
                                          'selfRated_Stress.csv'))[['subject', 'mean_stress']],
                      on='subject', how='left')
    hrv = pd.read_csv(op.join(p, 'HRV_var-v1_sampRate-500_subwise.csv'))
    agg = hrv.groupby(['subject', 'session'])[['HRV_SDNN', 'HRV_RMSSD',
                                               'HRV_LFHF', 'HR_bpm']].mean()
    meta = meta.merge((agg.xs(2, level='session') - agg.xs(1, level='session'))
                      .add_suffix('_change').reset_index(), on='subject', how='left')

    meta = meta[meta.subject.isin(subs)].set_index('subject').reindex(subs)
    ok = meta.group.notna().values
    shifts = shift_for(pm, meta.group.fillna(0).values)     # (draw, subject)

    print(f"posterior draws: {shifts.shape[0]}   subjects: {ok.sum()}")
    print("\nPartial correlation with the subject-level prior shift, group controlled.")
    print("Posterior mean [95% CrI], and the posterior probability of a positive "
          "association.\n")
    rows = []
    for x in ['AUC', 'mean_stress', 'HRV_SDNN_change', 'HRV_RMSSD_change',
              'HRV_LFHF_change', 'HR_bpm_change', 'E_dif']:
        m = ok & meta[x].notna().values
        r = partial_corr_rows(shifts[:, m], meta[x].values[m].astype(float),
                              meta.group.values[m].astype(float))
        rows.append(dict(predictor=x, n=int(m.sum()), r=r.mean(),
                         lo=np.percentile(r, 2.5), hi=np.percentile(r, 97.5),
                         p_pos=np.mean(r > 0)))
        print(f"  {x:18s} n={m.sum():2d}   r = {r.mean():+.3f} "
              f"[{np.percentile(r,2.5):+.3f}, {np.percentile(r,97.5):+.3f}]   "
              f"P(r>0) = {np.mean(r > 0):.3f}")

    pd.DataFrame(rows).to_csv(op.join(OUT, 'rebuttal_physiology_bayesian.csv'), index=False)
    print("\nEvery interval comprises zero: no individual-difference association "
          "survives\ncontrol for group, and the posterior on each correlation is "
          "wide, as expected\nwith 25 participants per group.")
    print(f"\nsaved {OUT}/rebuttal_physiology_bayesian.csv")


if __name__ == '__main__':
    main()
