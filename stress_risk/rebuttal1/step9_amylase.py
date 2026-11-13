"""Salivary alpha-amylase: the second stress marker in the assay file (R2.2).

Gokhan pointed out (2026-09-22) that the saliva assay measured alpha-amylase
alongside cortisol, and that the two index different systems: amylase is a fast
sympathetic/autonomic marker -- onset immediate, back to baseline in 15-20
minutes -- while cortisol is the slow glucocorticoid response. Participants were
re-stressed three times during the experiment, so the during-MIST samples are the
informative ones for amylase, and an AUC over all six samples is the wrong
summary for it even though it is the right one for cortisol.

Both markers live in addMeasures/auc_cortisol.xlsx (the name is misleading):
Cortisol_1/_2 and Amylase_1/_2 are duplicate assay runs of the same sample;
TimePoint is the sample's position within the participant, 1-6.

Sample timing, from the Methods and confirmed against the logged onsets:
    1  arrival                    (-40 min, not logged by the task computer)
    2  before the first MIST      (0 min)      = onset_Saliva_1
    3  during the second MIST     (~20 min)    = onset_Saliva_2
    4  during the third MIST      (~37 min)    = onset_Saliva_3
    5  end of the scan            (51 min)     = onset_Saliva_4
    6  after debriefing           (65 min)     = onset_Saliva_5
The nominal minutes are the intended protocol; the empirical medians printed by
timing_check() are what actually happened and run appreciably longer.
"""
import os.path as op
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg
import scipy.stats as ss

sys.path.insert(0, op.dirname(op.abspath(__file__)))
from common import BIDS_FOLDER  # noqa: E402
from step7_physiology_bayes import partial_corr_rows, shift_for, subject_shifts  # noqa: E402

OUT = '/Users/gdehol/git/stress_risk/notes/rebuttal1/results'
ADD = op.join(BIDS_FOLDER, 'addMeasures')
NOMINAL = {1: -40, 2: 0, 3: 20, 4: 37, 5: 51, 6: 65}      # minutes re stress onset
C_CTRL, C_STRESS, C_REF, C_INK = '#3B5BA5', '#C44E52', '#B0B0B0', '#2A2A2A'

mpl.rcParams.update({
    'font.family': 'Helvetica', 'font.sans-serif': ['Helvetica', 'Arial'],
    'font.size': 7, 'axes.labelsize': 8, 'axes.titlesize': 8,
    'xtick.labelsize': 7, 'ytick.labelsize': 7, 'legend.fontsize': 7,
    'axes.linewidth': 0.8, 'axes.spines.top': False, 'axes.spines.right': False,
    'xtick.direction': 'out', 'ytick.direction': 'out',
    'xtick.major.size': 3, 'ytick.major.size': 3,
    'xtick.major.width': 0.8, 'ytick.major.width': 0.8,
    'lines.linewidth': 1.2, 'legend.frameon': False,
    'pdf.fonttype': 42, 'ps.fonttype': 42, 'figure.dpi': 150, 'savefig.dpi': 300,
})


def load_saliva():
    """Long-format saliva: one row per (subject, sample), both markers averaged
    over their two assay runs."""
    d = pd.read_excel(op.join(ADD, 'auc_cortisol.xlsx'))
    d['cortisol'] = d[['Cortisol_1', 'Cortisol_2']].mean(1)
    d['amylase'] = d[['Amylase_1', 'Amylase_2']].mean(1)
    g = pd.read_csv(op.join(BIDS_FOLDER, 'group_assignmentList.csv'),
                    index_col=1)['group']
    d['group'] = d.SubjectID.map(g)
    return d.rename(columns={'SubjectID': 'subject', 'TimePoint': 'sample'})


def timing_check():
    """Confirm samples 2-6 against the logged onsets, and report what actually
    happened rather than the protocol's nominal minutes."""
    c = pd.read_excel(op.join(ADD, 'data_combined.xlsx'))
    ons = c[[f'onset_Saliva_{i}' for i in range(1, 6)]].apply(pd.to_datetime)
    off = ons.sub(ons['onset_Saliva_1'], axis=0).apply(
        lambda s: s.dt.total_seconds() / 60)
    med = off.median()
    print('  logged saliva onsets, minutes after the first logged one '
          '(= sample 2, the pre-MIST sample):')
    for i, (k, v) in enumerate(med.items(), start=2):
        print(f'    sample {i}  median {v:+6.1f} min   (protocol says '
              f'{NOMINAL[i]:+3d})')
    mist = c[[f'onset_MIST_{i}' for i in range(1, 4)]].median()
    print(f'  MIST block onsets, median minutes on the same clock: '
          f'{", ".join(f"{v:+.1f}" for v in mist)}')
    print('  Sample 1 (arrival, -40 min) is not logged by the task computer.')


def subject_level(d):
    """One row per participant: cortisol AUC, and two amylase summaries."""
    w = d.pivot_table(index='subject', columns='sample', values='amylase')
    cort = d.pivot_table(index='subject', columns='sample', values='cortisol')
    out = pd.DataFrame(index=w.index)
    out['group'] = d.groupby('subject')['group'].first()
    # cortisol AUC exactly as the shipped column: trapezoid over SAMPLE INDEX,
    # which ignores the unequal spacing between samples
    out['cort_auc'] = d.groupby('subject')['AUC'].first()
    full = w.notna().all(1)
    out['AA_auc'] = np.where(full, np.trapz(w.fillna(0).values, dx=1, axis=1), np.nan)
    # the summary that matches amylase kinetics: during-MIST rise over the
    # pre-MIST sample. Samples 3 and 4 are taken inside MIST blocks 2 and 3.
    out['AA_react'] = w[[3, 4]].mean(1) - w[2]
    out['AA_peak'] = w[[2, 3, 4, 5, 6]].max(1) - w[2]
    out['cort_react'] = cort[[4, 5]].mean(1) - cort[2]
    return out, w, cort


def group_curves(d):
    """Per-sample group contrast on each marker."""
    for marker in ['cortisol', 'amylase']:
        print(f'\n  {marker} by sample (mean +- SEM), and the group contrast:')
        for s in sorted(d['sample'].unique()):
            x = d[(d['sample'] == s)]
            a = x.loc[x.group == 1, marker].dropna()
            b = x.loc[x.group == 0, marker].dropna()
            t, p = ss.ttest_ind(a, b, equal_var=False)
            print(f'    sample {s} ({NOMINAL[s]:+3d} min)  stress '
                  f'{a.mean():7.1f}+-{a.sem():5.1f} (n={len(a)})   control '
                  f'{b.mean():7.1f}+-{b.sem():5.1f} (n={len(b)})   '
                  f't={t:+5.2f}  p={p:.3f}')


def omnibus(d):
    """Group x sample mixed ANOVA on each marker.

    Amylase is strongly right-skewed and conventionally analysed on a log scale;
    both are reported so the transform cannot be the thing doing the work. The
    ANOVA needs complete cases, so n drops - the per-sample contrasts above use
    everyone available at each sample.
    """
    for marker, tf in [('cortisol', None), ('amylase', None), ('amylase', np.log)]:
        w = d.pivot_table(index='subject', columns='sample', values=marker).dropna()
        lab = f'{marker}{" (log)" if tf is not None else ""}'
        long = (w.apply(tf) if tf is not None else w).stack().rename('y').reset_index()
        long['group'] = long.subject.map(d.groupby('subject')['group'].first())
        a = pg.mixed_anova(long, dv='y', within='sample', between='group',
                           subject='subject')
        g = a.set_index('Source')
        print(f'    {lab:16s} n={len(w):2d}   group F={g.loc["group", "F"]:5.2f} '
              f'p={g.loc["group", "p-unc"]:.3f}   sample F='
              f'{g.loc["sample", "F"]:5.2f} p={g.loc["sample", "p-unc"]:.3f}   '
              f'group x sample F={g.loc["Interaction", "F"]:5.2f} '
              f'p={g.loc["Interaction", "p-unc"]:.3f}')


def summaries(sub):
    print('\n  Subject-level summaries, group contrast:')
    for k, lab in [('cort_auc', 'Cortisol AUC (over sample index)'),
                   ('cort_react', 'Cortisol rise, samples 4-5 minus 2'),
                   ('AA_auc', 'Amylase AUC (over sample index)'),
                   ('AA_react', 'Amylase rise, samples 3-4 minus 2'),
                   ('AA_peak', 'Amylase peak rise over sample 2')]:
        a = sub.loc[sub.group == 1, k].dropna()
        b = sub.loc[sub.group == 0, k].dropna()
        t, p = ss.ttest_ind(a, b, equal_var=False)
        bf = float(pg.ttest(a, b, correction=True)['BF10'].iloc[0])
        print(f'    {lab:38s} stress {a.mean():8.2f}  control {b.mean():8.2f}  '
              f't={t:+5.2f}  p={p:.3f}  BF10={bf:.2f}  (n={len(a)}/{len(b)})')


def correlations(sub):
    """Does the amylase response predict the size of an individual's prior shift?

    Two estimates of the same thing, as elsewhere in this rebuttal: the partial
    correlation computed once per posterior draw of the participant-level shifts
    (carrying their uncertainty), and the frequentist partial correlation on the
    posterior means, which is what the reply letter quotes.
    """
    pm, subs = subject_shifts()
    meta = sub.reindex(subs)
    shifts = shift_for(pm, meta.group.fillna(0).values)        # (draw, subject)
    prior = pd.read_csv(op.join(BIDS_FOLDER, 'interim_sum_data',
                                'commonPriorShift-model5_Ediff_AUC.csv'))
    prior = prior.set_index('subject').reindex(subs)

    print('\n  Partial correlation with the participant-level prior shift, '
          'group controlled.')
    print('  Per posterior draw [95% CrI], then the point-estimate version '
          '(r, p):\n')
    rows = []
    for k in ['cort_auc', 'cort_react', 'AA_auc', 'AA_react', 'AA_peak']:
        # keep the sample identical to the rest of the rebuttal: the 49 participants
        # carried by commonPriorShift-model5_Ediff_AUC.csv, so the per-draw and the
        # point-estimate version of each row are computed on the same people
        m = (meta.group.notna().values & meta[k].notna().values
             & prior['prior_shift'].notna().values)
        r = partial_corr_rows(shifts[:, m], meta[k].values[m].astype(float),
                              meta.group.values[m].astype(float))
        s = pd.DataFrame({'y': prior['prior_shift'].values[m],
                          'x': meta[k].values[m].astype(float),
                          'group': meta.group.values[m].astype(float)}).dropna()
        pr = pg.partial_corr(s, x='x', y='y', covar='group')
        zero = pg.corr(s.x, s.y)
        rows.append(dict(measure=k, n=int(m.sum()), r_draws=r.mean(),
                         lo=np.percentile(r, 2.5), hi=np.percentile(r, 97.5),
                         p_pos=np.mean(r > 0), r_zero=zero['r'].iloc[0],
                         p_zero=zero['p-val'].iloc[0],
                         r_partial=pr['r'].iloc[0], p_partial=pr['p-val'].iloc[0]))
        print(f'    {k:11s} n={m.sum():2d}   r = {r.mean():+.3f} '
              f'[{np.percentile(r, 2.5):+.3f}, {np.percentile(r, 97.5):+.3f}]   '
              f'P(r>0) = {np.mean(r > 0):.3f}   |   zero-order r = '
              f'{zero["r"].iloc[0]:+.3f} (p = {zero["p-val"].iloc[0]:.3f}), '
              f'partial r = {pr["r"].iloc[0]:+.3f} (p = {pr["p-val"].iloc[0]:.3f})')
    t = pd.DataFrame(rows)
    t.to_csv(op.join(OUT, 'rebuttal_amylase_correlations.csv'), index=False)

    c = sub[['cort_auc', 'cort_react', 'AA_auc', 'AA_react']].dropna()
    print(f'\n  Cortisol AUC vs amylase rise, across participants: '
          f'r = {c.corr().loc["cort_auc", "AA_react"]:+.3f} '
          f'(n = {len(c)}) - the two markers are close to independent.')
    return t


def stars(p):
    """Conventional markers. Uncorrected across the six samples - with two
    markers and six samples that is twelve tests, so read them as descriptive."""
    return '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else ''


def figure(d):
    """Both markers over the six samples, by group."""
    fig, axs = plt.subplots(1, 2, figsize=(5.2, 2.3), constrained_layout=True)
    x = np.array([NOMINAL[s] for s in range(1, 7)])
    for ax, marker, lab in [(axs[0], 'cortisol', 'Salivary cortisol (nmol/l)'),
                            (axs[1], 'amylase', 'Salivary alpha-amylase (U/ml)')]:
        top = {}
        for grp, col, name in [(0, C_CTRL, 'Control'), (1, C_STRESS, 'Stress')]:
            w = (d[d.group == grp].pivot_table(index='subject', columns='sample',
                                               values=marker)
                 .reindex(columns=range(1, 7)))
            m, se = w.mean(), w.sem()
            ax.fill_between(x, m - se, m + se, color=col, alpha=.18, lw=0)
            ax.plot(x, m, 'o-', color=col, ms=3.2, label=name)
            top[grp] = (m + se).values
        for t0 in [0, 20, 37]:                     # the three MIST blocks
            ax.axvline(t0, color=C_REF, lw=.7, ls=':', zorder=0)
        ax.set_xticks(x)
        ax.set_xlabel('Time relative to stress onset (min)')
        ax.set_ylabel(lab)

        hi = np.maximum(top[0], top[1])
        pad = .04 * np.ptp(ax.get_ylim())
        for i, s in enumerate(range(1, 7)):
            a = d.loc[(d['sample'] == s) & (d.group == 1), marker].dropna()
            b = d.loc[(d['sample'] == s) & (d.group == 0), marker].dropna()
            mark = stars(ss.ttest_ind(a, b, equal_var=False).pvalue)
            if mark:
                ax.annotate(mark, (x[i], hi[i] + pad), ha='center', va='bottom',
                            fontsize=8, color=C_INK)
        ax.set_ylim(top=ax.get_ylim()[1] + 2 * pad)
    axs[0].legend(loc='upper left')
    axs[0].set_title('Slow: glucocorticoid', color=C_INK)
    axs[1].set_title('Fast: autonomic', color=C_INK)
    for ext in ['pdf', 'png']:
        fig.savefig(op.join(OUT, f'fig_saliva_markers.{ext}'),
                    bbox_inches='tight', pad_inches=.02,
                    **({'dpi': 220} if ext == 'png' else {}))
    print(f'\n  wrote {OUT}/fig_saliva_markers.pdf/.png')


def main():
    d = load_saliva()
    print(f'saliva assay: {d.subject.nunique()} participants x '
          f'{d["sample"].nunique()} samples; missing amylase values: '
          f'{d.amylase.isna().sum()}, cortisol: {d.cortisol.isna().sum()}')
    print('\n=== Sample timing ===')
    timing_check()
    print('\n=== Group curves ===')
    group_curves(d)
    print('\n=== Group x sample, omnibus ===')
    omnibus(d)
    sub, _, _ = subject_level(d)
    summaries(sub)
    print('\n=== Association with the behavioural effect ===')
    correlations(sub)
    sub.to_csv(op.join(OUT, 'rebuttal_amylase_subjectwise.csv'))
    print(f'  wrote {OUT}/rebuttal_amylase_subjectwise.csv')
    figure(d)


if __name__ == '__main__':
    main()
