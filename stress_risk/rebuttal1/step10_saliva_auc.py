"""Proper AUC analysis of the saliva curves, on real elapsed time (R2.2).

The AUC column shipped in addMeasures/auc_cortisol.xlsx -- the one the paper
reports and that every correlation in this rebuttal uses -- turns out to be the
area under the CIRCADIAN-CORRECTED curve over samples 2-6, i.e. the trapezoid of
(cortisol - estCircadianChange) integrated against the sample's POSITION, 2..6.
Reproduced here to r = 0.998 (see `reproduce_shipped`). Correcting for the
circadian decline is right; integrating against position is not. The samples are
not equally spaced: the logged medians are -40, 0, +33, +55, +70, +79 minutes,
gaps of 40, 33, 22, 15 and 8 minutes. Weighting an 8-minute gap the same as a
40-minute one distorts the summary, and does so differently for a slow marker
than for a fast one.

Here both markers are integrated against each participant's OWN logged sample
times, in the two forms Pruessner et al. (2003) define:

    AUCg  area under the curve with respect to ground   - total output
    AUCi  area with respect to increase, = AUCg minus the baseline rectangle
          - the reactivity measure, and the one the reviewer's question is about

Two windows, because they answer different questions and have different
missing-data costs:

    full   samples 1-6, baseline = sample 1 (arrival). Sample 1 has no logged
           onset, so it is placed at the protocol's -40 min; every other sample
           uses that participant's logged clock time.
    MIST   samples 2-6, baseline = sample 2 (immediately before the first MIST).
           Fully logged, no imputed time, and it isolates the manipulation from
           the arrival response.
"""
import os.path as op
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg
import scipy.stats as ss

sys.path.insert(0, op.dirname(op.abspath(__file__)))
from common import BIDS_FOLDER  # noqa: E402
from step7_physiology_bayes import partial_corr_rows, shift_for, subject_shifts  # noqa: E402
from step9_amylase import (ADD, C_CTRL, C_REF, C_INK, C_STRESS, OUT,  # noqa: E402
                           load_saliva, stars)

ARRIVAL = -40.0            # protocol time of sample 1; the only imputed number here


def sample_times():
    """(subject x sample) matrix of minutes relative to the first MIST.

    Samples 2-6 are the logged saliva onsets; sample 1 is the unlogged arrival
    sample and is placed at the protocol's -40 min.
    """
    c = pd.read_excel(op.join(ADD, 'data_combined.xlsx')).set_index('SUBID')
    ons = c[[f'onset_Saliva_{i}' for i in range(1, 6)]].apply(pd.to_datetime)
    off = ons.sub(ons['onset_Saliva_1'], axis=0).apply(
        lambda s: s.dt.total_seconds() / 60)
    off.columns = range(2, 7)
    off.insert(0, 1, ARRIVAL)
    off.index.name = 'subject'
    return off


def auc(values, times):
    """Trapezoidal AUCg and AUCi over one participant's curve.

    Returns (nan, nan) unless every sample in the window is present -- an AUC
    over a curve with a hole in it is not comparable across participants.
    """
    v, t = np.asarray(values, float), np.asarray(times, float)
    if np.isnan(v).any() or np.isnan(t).any():
        return np.nan, np.nan
    g = np.trapz(v, t)
    return g, g - v[0] * (t[-1] - t[0])


def build(d, times):
    """Per-participant AUCg/AUCi for both markers, in both windows."""
    out = pd.DataFrame(index=sorted(d.subject.unique()))
    out.index.name = 'subject'
    out['group'] = d.groupby('subject')['group'].first()
    out['auc_index_shipped'] = d.groupby('subject')['AUC'].first()

    # the paper's measure and its time-based counterpart: cortisol minus the
    # estimated circadian decline, integrated over samples 2-6 against the sample
    # index (as shipped) and against the logged minutes (as it should be)
    cols = [2, 3, 4, 5, 6]
    obs = d.pivot_table(index='subject', columns='sample', values='cortisol')
    est = d.pivot_table(index='subject', columns='sample',
                        values='estCircadianChange')
    corr_ = (obs[cols] - est.reindex(columns=cols)).reindex(out.index)
    out['cort_cc_idx'] = [np.trapz(r.values, cols) if r.notna().all() else np.nan
                          for _, r in corr_.iterrows()]
    out['cort_cc_min'] = [
        np.trapz(corr_.loc[s].values, times.loc[s, cols].values)
        if (s in times.index and corr_.loc[s].notna().all()) else np.nan
        for s in out.index]
    for marker in ['cortisol', 'amylase']:
        w = d.pivot_table(index='subject', columns='sample', values=marker)
        for tag, cols in [('full', [1, 2, 3, 4, 5, 6]), ('mist', [2, 3, 4, 5, 6])]:
            g, i = [], []
            for s in out.index:
                t = times.loc[s, cols].values if s in times.index else np.full(len(cols), np.nan)
                a, b = auc(w.loc[s, cols].values, t)
                g.append(a), i.append(b)
            out[f'{marker[:4]}_{tag}_g'] = g
            out[f'{marker[:4]}_{tag}_i'] = i
    return out


LABEL = {'cort_cc_idx': 'Cortisol AUCcc, index (paper)',
         'cort_cc_min': 'Cortisol AUCcc, minutes',
         'cort_full_g': 'Cortisol AUCg, samples 1-6',
         'cort_full_i': 'Cortisol AUCi, samples 1-6',
         'cort_mist_g': 'Cortisol AUCg, samples 2-6',
         'cort_mist_i': 'Cortisol AUCi, samples 2-6',
         'amyl_full_g': 'Amylase AUCg, samples 1-6',
         'amyl_full_i': 'Amylase AUCi, samples 1-6',
         'amyl_mist_g': 'Amylase AUCg, samples 2-6',
         'amyl_mist_i': 'Amylase AUCi, samples 2-6'}


def contrasts(a):
    print('\n  Group contrast on each AUC (Welch t, and BF10):')
    rows = []
    for k, lab in LABEL.items():
        x1 = a.loc[a.group == 1, k].dropna()
        x0 = a.loc[a.group == 0, k].dropna()
        t, p = ss.ttest_ind(x1, x0, equal_var=False)
        bf = float(pg.ttest(x1, x0, correction=True)['BF10'].iloc[0])
        dz = pg.compute_effsize(x1, x0, eftype='cohen')
        rows.append(dict(measure=k, n_stress=len(x1), n_control=len(x0),
                         mean_stress=x1.mean(), mean_control=x0.mean(),
                         t=t, p=p, BF10=bf, cohen_d=dz))
        print(f'    {lab:30s} stress {x1.mean():9.1f}  control {x0.mean():9.1f}  '
              f't={t:+5.2f}  p={p:.3f}  BF10={bf:8.2f}  d={dz:+.2f}  '
              f'(n={len(x1)}/{len(x0)})')
    return pd.DataFrame(rows)


def against_shipped(a):
    s = a[['auc_index_shipped', 'cort_cc_idx', 'cort_cc_min', 'cort_full_g',
           'cort_full_i', 'cort_mist_i']].dropna()
    print(f'\n  Reproducing the shipped AUC column (n = {len(s)}): '
          f'r = {s["auc_index_shipped"].corr(s["cort_cc_idx"]):+.4f} with the '
          'circadian-corrected\n  trapezoid over sample index 2-6 - that is what '
          'it is.')
    print('\n  The shipped column vs the alternatives:')
    for k in ['cort_cc_min', 'cort_full_g', 'cort_full_i', 'cort_mist_i']:
        print(f'    shipped vs {LABEL[k]:30s} r = '
              f'{s["auc_index_shipped"].corr(s[k]):+.3f}')


def correlations(a):
    """Group-controlled association with the participant-level prior shift."""
    pm, subs = subject_shifts()
    meta = a.reindex(subs)
    shifts = shift_for(pm, meta.group.fillna(0).values)
    prior = pd.read_csv(op.join(BIDS_FOLDER, 'interim_sum_data',
                                'commonPriorShift-model5_Ediff_AUC.csv'))
    prior = prior.set_index('subject').reindex(subs)

    print('\n  Partial correlation with the prior shift, group controlled.')
    print('  Per posterior draw [95% CrI], then the point-estimate version:\n')
    rows = []
    for k, lab in LABEL.items():
        m = (meta.group.notna().values & meta[k].notna().values
             & prior['prior_shift'].notna().values)
        r = partial_corr_rows(shifts[:, m], meta[k].values[m].astype(float),
                              meta.group.values[m].astype(float))
        s = pd.DataFrame({'y': prior['prior_shift'].values[m],
                          'x': meta[k].values[m].astype(float),
                          'group': meta.group.values[m].astype(float)}).dropna()
        pr = pg.partial_corr(s, x='x', y='y', covar='group')
        rows.append(dict(measure=k, n=int(m.sum()), r_draws=r.mean(),
                         lo=np.percentile(r, 2.5), hi=np.percentile(r, 97.5),
                         p_pos=np.mean(r > 0), r_partial=pr['r'].iloc[0],
                         p_partial=pr['p-val'].iloc[0]))
        print(f'    {lab:30s} n={m.sum():2d}  r = {r.mean():+.3f} '
              f'[{np.percentile(r, 2.5):+.3f}, {np.percentile(r, 97.5):+.3f}]  '
              f'P(r>0) = {np.mean(r > 0):.3f}  |  partial r = '
              f'{pr["r"].iloc[0]:+.3f} (p = {pr["p-val"].iloc[0]:.3f})')
    return pd.DataFrame(rows)


def figure(a):
    """AUCg and AUCi by group, both markers, participants shown individually."""
    keys = ['cort_cc_idx', 'cort_cc_min', 'amyl_full_g', 'amyl_mist_i']
    titles = ['Cortisol AUC\n(paper: sample index)',
              'Cortisol AUC\n(logged minutes)',
              'Amylase AUCg\n(samples 1-6)', 'Amylase AUCi\n(samples 2-6)']
    units = ['nmol/l x sample', 'nmol/l x min', 'U/ml x min', 'U/ml x min']
    fig, axs = plt.subplots(1, 4, figsize=(6.6, 2.2), constrained_layout=True)
    rng = np.random.default_rng(0)
    for ax, k, ti, un in zip(axs, keys, titles, units):
        tops = []
        for j, (grp, col) in enumerate([(0, C_CTRL), (1, C_STRESS)]):
            v = a.loc[a.group == grp, k].dropna().values
            ax.scatter(j + rng.uniform(-.13, .13, len(v)), v, s=5, color=col,
                       alpha=.45, lw=0)
            ax.errorbar(j, v.mean(), ss.sem(v), fmt='o', color=col, ms=4,
                        capsize=2.5, lw=1.1, mec='white', mew=.6, zorder=5)
            tops.append(v.max())
        ax.axhline(0, color=C_REF, lw=.7, ls=':', zorder=0)
        x1 = a.loc[a.group == 1, k].dropna()
        x0 = a.loc[a.group == 0, k].dropna()
        p = ss.ttest_ind(x1, x0, equal_var=False).pvalue
        mark = stars(p) or 'n.s.'
        y = max(tops) + .06 * np.ptp(ax.get_ylim())
        ax.plot([0, 1], [y, y], color=C_INK, lw=.8)
        ax.annotate(mark, (.5, y), ha='center', va='bottom', fontsize=7,
                    color=C_INK)
        ax.set_ylim(top=y + .16 * np.ptp(ax.get_ylim()))
        ax.set_xticks([0, 1]); ax.set_xticklabels(['Control', 'Stress'])
        ax.set_xlim(-.5, 1.5)
        ax.set_title(ti); ax.set_ylabel(un)
    for ext in ['pdf', 'png']:
        fig.savefig(op.join(OUT, f'fig_saliva_auc.{ext}'), bbox_inches='tight',
                    pad_inches=.02, **({'dpi': 220} if ext == 'png' else {}))
    print(f'\n  wrote {OUT}/fig_saliva_auc.pdf/.png')


def main():
    d = load_saliva()
    times = sample_times()
    med = times.median()
    print('sample times used (median over participants, minutes re first MIST):')
    print('  ' + '  '.join(f'{s}: {med[s]:+.1f}' for s in med.index)
          + '      [sample 1 imputed at the protocol value]')
    print(f'  gaps: {"  ".join(f"{g:.0f}" for g in np.diff(med.values))} minutes '
          '- the index-based AUC treats these as equal')

    a = build(d, times)
    print(f'\nparticipants with a complete curve: '
          f'cortisol {a.cort_full_g.notna().sum()} (samples 1-6), '
          f'{a.cort_mist_g.notna().sum()} (samples 2-6); '
          f'amylase {a.amyl_full_g.notna().sum()} / {a.amyl_mist_g.notna().sum()}')
    contrasts(a).to_csv(op.join(OUT, 'rebuttal_saliva_auc_contrasts.csv'),
                        index=False)
    against_shipped(a)
    correlations(a).to_csv(op.join(OUT, 'rebuttal_saliva_auc_correlations.csv'),
                           index=False)
    a.to_csv(op.join(OUT, 'rebuttal_saliva_auc_subjectwise.csv'))
    print(f'\n  wrote {OUT}/rebuttal_saliva_auc_contrasts.csv, '
          f'_correlations.csv, _subjectwise.csv')
    figure(a)


if __name__ == '__main__':
    main()
