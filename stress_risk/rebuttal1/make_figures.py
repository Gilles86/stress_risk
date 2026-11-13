"""Figures for the reviewer-response analyses.

  fig_baseline_contrasts  - R1.3: session-1 group contrast on all six PMC
                            parameters, and how each compares with its own
                            group x session interaction.
  fig_neural_riskysafe    - R1.2: why numerosity matching is necessary, and the
                            three matched comparisons.
  fig_correlations        - R2.2 / R1 minor: posterior partial correlations.
"""
import os.path as op
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sys.path.insert(0, op.dirname(op.abspath(__file__)))
from common import BIDS_FOLDER, PMCParams, design, softplus  # noqa: E402
from step6_baseline import PARAMS, population_cell, subject_values  # noqa: E402
from step7_physiology_bayes import partial_corr_rows, subject_shifts  # noqa: E402

OUT = '/Users/gdehol/git/stress_risk/notes/rebuttal1/results'
C_SAFE, C_RISKY, C_REF, C_INK = '#3B5BA5', '#C44E52', '#B0B0B0', '#2A2A2A'

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
LABEL = {'risky_prior_mu': 'Risky prior mean', 'safe_prior_mu': 'Safe prior mean',
         'risky_prior_std': 'Risky prior width', 'safe_prior_std': 'Safe prior width',
         'n1_evidence_sd': 'Evidence noise, 1st', 'n2_evidence_sd': 'Evidence noise, 2nd'}


def save(fig, name):
    fig.savefig(op.join(OUT, name + '.pdf'), bbox_inches='tight', pad_inches=.02)
    fig.savefig(op.join(OUT, name + '.png'), dpi=220, bbox_inches='tight', pad_inches=.02)
    print('  wrote', name)


# ------------------------------------------------------------------ figure 1
def baseline_figure():
    P = PMCParams()
    grp = (pd.read_csv(op.join(BIDS_FOLDER, 'group_assignmentList.csv'),
                       index_col=1)['group'].reindex(P.subjects).values)
    base, inter, sd = {}, {}, {}
    for par in PARAMS:
        base[par] = population_cell(P, par, 1, 1) - population_cell(P, par, 1, 0)
        inter[par] = ((population_cell(P, par, 2, 1) - population_cell(P, par, 1, 1))
                      - (population_cell(P, par, 2, 0) - population_cell(P, par, 1, 0)))
        # between-subject SD computed PER DRAW, then averaged: standardising by the
        # SD of posterior means would divide by a shrunk quantity and inflate the
        # standardised gaps.
        sd[par] = subject_values(P, par, 1, grp).std(axis=1, ddof=1).mean()

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(7.1, 2.5), constrained_layout=True,
                                   gridspec_kw=dict(width_ratios=[1.25, 1]))
    y = np.arange(len(PARAMS))[::-1]
    ax0.axvline(0, color=C_REF, lw=.8, ls='--', zorder=0)
    for i, par in enumerate(PARAMS):
        d = base[par] / sd[par]           # standardised on the between-subject scale
        lo, hi = np.percentile(d, [2.5, 97.5])
        q1, q3 = np.percentile(d, [25, 75])
        ax0.plot([lo, hi], [y[i]] * 2, color=C_INK, lw=1.0, solid_capstyle='butt')
        ax0.plot([q1, q3], [y[i]] * 2, color=C_INK, lw=2.6, solid_capstyle='butt')
        ax0.plot(d.mean(), y[i], 'o', color='white', mec=C_INK, mew=1.1, ms=5, zorder=5)
    ax0.set_yticks(y); ax0.set_yticklabels([LABEL[p] for p in PARAMS])
    ax0.set_xlabel('Session-1 group difference (stress − control)\nin between-subject SD')
    ax0.set_xlim(-1.2, 1.2)
    ax0.set_ylim(y[-1] - .6, y[0] + 1.15)
    ax0.set_title('No parameter differs credibly at baseline', fontsize=7.5, pad=5)

    ratio = [abs(base[p].mean()) / abs(inter[p].mean()) for p in PARAMS]
    cols = [C_SAFE if r < .2 else C_RISKY for r in ratio]
    ax1.axvspan(1, 3.4, color=C_RISKY, alpha=.07, lw=0, zorder=0)
    ax1.axvline(1, color=C_REF, lw=.8, ls='--', zorder=1)
    ax1.barh(y, np.clip(ratio, 0, 3), color=cols, height=.55, alpha=.85, zorder=2)
    for i, r in enumerate(ratio):
        ax1.text(min(r, 3) + .07, y[i], f'{r:.2f}', va='center', ha='left',
                 fontsize=6.5, color=cols[i])
    ax1.set_yticks(y); ax1.set_yticklabels([])
    ax1.set_xlim(0, 3.4); ax1.set_xticks([0, 1, 2, 3])
    ax1.set_xlabel('Baseline gap ÷ the group × session effect')
    ax1.set_title('Could the baseline gap have produced the effect?', fontsize=7.5, pad=5)
    ax1.text(.97, y[0] + .5, 'effect bigger\nthan the gap', fontsize=6.2, color='0.45',
             ha='right', va='center', linespacing=1.3)
    ax1.text(1.06, y[0] + .5, 'gap bigger\nthan the effect', fontsize=6.2, color=C_RISKY,
             ha='left', va='center', linespacing=1.3)
    ax1.annotate('The prior mean carries the reported\neffect: the baseline gap is 3% of it',
                 xy=(0.05, y[0]), xytext=(1.25, y[1] - .55), fontsize=6.4, color=C_SAFE,
                 ha='left', va='center', linespacing=1.35,
                 arrowprops=dict(arrowstyle='-|>', color=C_SAFE, lw=.8, mutation_scale=6,
                                 shrinkA=3, shrinkB=4, relpos=(0., .5),
                                 connectionstyle='angle3,angleA=0,angleB=70'))
    ax1.set_ylim(y[-1] - .6, y[0] + 1.15)
    sns.despine(fig=fig, offset=4)
    save(fig, 'fig_baseline_contrasts')


# ------------------------------------------------------------------ figure 2
def neural_figure():
    d = pd.read_csv(op.join(OUT, 'rebuttal_neural_matched_trials.csv'))
    exact = sorted(set(d.loc[d.option == 'risky', 'n1']) & set(d.loc[d.option == 'safe', 'n1']))
    e = d[d.n1.isin(exact)]
    fig, axes = plt.subplots(1, 4, figsize=(7.25, 2.15), constrained_layout=True)

    ax = axes[0]
    for opt, col in [('risky', C_RISKY), ('safe', C_SAFE)]:
        v = d.loc[d.option == opt, 'n1']
        ax.hist(v, bins=np.arange(6.5, 30.5, 1), color=col, alpha=.55, label=opt.capitalize())
    ax.set_xlabel('First-option payoff (coins)'); ax.set_ylabel('Trials')
    ax.set_title('Why matching is needed', fontsize=7.5, pad=4)
    ax.text(.97, .95, 'Safe takes only\n5 values', transform=ax.transAxes, ha='right',
            va='top', fontsize=6.5, color='0.35', linespacing=1.3)
    ax.text(.97, .62, 'Risky', transform=ax.transAxes, ha='right', va='top',
            fontsize=7, color=C_RISKY)

    for ax, (col_, lab, ttl) in zip(axes[1:], [
            ('E_dif', 'Shift in neural coding', 'Neural shift (both groups)'),
            ('err', 'Decoding error (log units)', 'Decoding error'),
            ('sd_within', 'Posterior width', 'Decoded precision')]):
        s = e.groupby(['subject', 'n1', 'option'])[col_].mean().unstack().dropna()
        s = s.groupby('subject').mean()
        for i, (opt, col) in enumerate([('safe', C_SAFE), ('risky', C_RISKY)]):
            x = np.random.default_rng(0).normal(i, .055, len(s))
            ax.plot(x, s[opt], 'o', color=col, ms=2.6, alpha=.35, mew=0)
            ax.plot([i - .22, i + .22], [s[opt].mean()] * 2, color=col, lw=2)
            se = s[opt].std(ddof=1) / np.sqrt(len(s))
            ax.plot([i, i], [s[opt].mean() - se, s[opt].mean() + se], color=col, lw=1.4)
        for j in range(len(s)):
            ax.plot([0, 1], [s['safe'].iloc[j], s['risky'].iloc[j]], color='0.75',
                    lw=.35, zorder=0)
        ax.set_xticks([0, 1]); ax.set_xticklabels(['Safe', 'Risky'])
        ax.set_xlim(-.45, 1.45); ax.set_ylabel(lab)
        ax.set_title(ttl, fontsize=7.5, pad=4)
    axes[1].text(.5, .02, 'matched on exact payoff', transform=axes[1].transAxes,
                 ha='center', va='bottom', fontsize=6.5, color='0.45')
    sns.despine(fig=fig, offset=4)
    save(fig, 'fig_neural_riskysafe')


# ------------------------------------------------------------------ figure 3
def correlation_figure():
    pm, subs = subject_shifts()
    p = op.join(BIDS_FOLDER, 'interim_sum_data')
    meta = pd.read_csv(op.join(p, 'commonPriorShift-model5_Ediff_AUC.csv'))
    meta = meta.merge(pd.read_csv(op.join(BIDS_FOLDER, 'addMeasures',
                                          'selfRated_Stress.csv'))[['subject', 'mean_stress']],
                      on='subject', how='left')
    hrv = pd.read_csv(op.join(p, 'HRV_var-v1_sampRate-500_subwise.csv'))
    agg = hrv.groupby(['subject', 'session'])[['HRV_SDNN', 'HRV_RMSSD', 'HRV_LFHF',
                                               'HR_bpm']].mean()
    meta = meta.merge((agg.xs(2, level='session') - agg.xs(1, level='session'))
                      .add_suffix('_change').reset_index(), on='subject', how='left')
    meta = meta[meta.subject.isin(subs)].set_index('subject').reindex(subs)
    ok = meta.group.notna().values
    d = np.stack([design(2, g, False) - design(1, g, False)
                  for g in meta.group.fillna(0).values])
    shifts = np.einsum('dsr,sr->ds', pm, d)

    names = {'AUC': 'Cortisol AUC', 'mean_stress': 'Self-rated stress',
             'E_dif': 'Neural shift', 'HRV_SDNN_change': 'HRV SDNN',
             'HRV_RMSSD_change': 'HRV RMSSD', 'HRV_LFHF_change': 'HRV LF/HF',
             'HR_bpm_change': 'Mean heart rate'}
    fig, ax = plt.subplots(figsize=(4.0, 2.6), constrained_layout=True)
    ax.axvline(0, color=C_REF, lw=.8, ls='--', zorder=0)
    y = np.arange(len(names))[::-1]
    for i, (k, lab) in enumerate(names.items()):
        m = ok & meta[k].notna().values
        r = partial_corr_rows(shifts[:, m], meta[k].values[m].astype(float),
                              meta.group.values[m].astype(float))
        lo, hi = np.percentile(r, [2.5, 97.5]); q1, q3 = np.percentile(r, [25, 75])
        ax.plot([lo, hi], [y[i]] * 2, color=C_INK, lw=1.0)
        ax.plot([q1, q3], [y[i]] * 2, color=C_INK, lw=2.6)
        ax.plot(r.mean(), y[i], 'o', color='white', mec=C_INK, mew=1.1, ms=5, zorder=5)
    ax.set_yticks(y); ax.set_yticklabels(list(names.values()))
    ax.set_xlim(-.6, .6); ax.set_xlabel('Partial correlation with the prior shift\n'
                                        '(group controlled)')
    sns.despine(fig=fig, offset=4)
    save(fig, 'fig_correlations')




# ------------------------------------------------------------------ figure 4
def parameter_figure():
    """All six group-level parameters: groups on x, value on y.

    The two session-1 cells sit side by side so the baseline comparison - the one
    the reviewer asks about - is read directly, with the posterior probability of a
    group difference printed above each session pair.
    """
    from scipy.stats import gaussian_kde
    P = PMCParams()
    # x positions: control/stress within session 1, then within session 2
    CELLS = [(0, 1, 0.0), (1, 1, 0.85), (0, 2, 2.25), (1, 2, 3.10)]
    COL = {0: C_SAFE, 1: C_RISKY}
    UNITS = {'risky_prior_mu': 'log coins', 'safe_prior_mu': 'log coins',
             'risky_prior_std': 'log units', 'safe_prior_std': 'log units',
             'n1_evidence_sd': 'log units', 'n2_evidence_sd': 'log units'}
    # objective statistics of the payoffs actually presented (value_events files
    # excluded - they are the value-GLM event files and carry different payoffs)
    OBJ = {'risky_prior_mu': 3.353, 'safe_prior_mu': 2.643,
           'risky_prior_std': 0.602, 'safe_prior_std': 0.490}

    fig, axes = plt.subplots(2, 3, figsize=(7.25, 4.9), constrained_layout=True)
    for ax, par in zip(axes.ravel(), PARAMS):
        draws = {}
        for g, s_, xp in CELLS:
            d = population_cell(P, par, s_, g); draws[(g, s_)] = d
            ys = np.linspace(np.percentile(d, .5), np.percentile(d, 99.5), 200)
            dens = gaussian_kde(d)(ys); dens = .34 * dens / dens.max()
            ax.fill_betweenx(ys, xp - dens, xp + dens, color=COL[g],
                             alpha=.55 if s_ == 2 else .22, lw=0)
            lo, hi = np.percentile(d, [2.5, 97.5])
            ax.plot([xp, xp], [lo, hi], color=COL[g], lw=.9)
            ax.plot(xp, d.mean(), 'o', color='white', mec=COL[g], mew=1.1, ms=4, zorder=5)

        if par in OBJ:
            ax.axhline(OBJ[par], color='0.45', lw=.8, ls=':', zorder=0)

        # Two contrasts, and they answer different questions. The session-1 bracket
        # is the cross-sectional baseline check the reviewer asks about. The wide
        # bracket is the group x session interaction - the effect the paper
        # reports, and a within-subject contrast, so the between-participant
        # spread that inflates a cross-sectional comparison cancels out. A
        # session-2 cross-sectional bracket would be neither and reads as a much
        # weaker version of the effect (P = 0.95 against 0.998 for the prior mean).
        top = max(np.percentile(draws[k], 99.5) for k in draws)
        bot = min(np.percentile(draws[k], .5) for k in draws)
        pad = (top - bot)

        base = draws[(1, 1)] - draws[(0, 1)]
        yb = top + .09 * pad
        ax.plot([0.0, 0.0, 0.85, 0.85], [yb - .03 * pad, yb, yb, yb - .03 * pad],
                color='0.45', lw=.7, clip_on=False)
        ax.text(0.425, yb + .02 * pad, f'baseline P = {np.mean(base > 0):.2f}',
                ha='center', va='bottom', fontsize=6.2, color='0.35', clip_on=False)

        inter = ((draws[(1, 2)] - draws[(1, 1)]) - (draws[(0, 2)] - draws[(0, 1)]))
        pi = np.mean(inter > 0)
        pi = max(pi, 1 - pi)
        yi = top + .30 * pad
        ax.plot([0.0, 0.0, 3.10, 3.10], [yi - .03 * pad, yi, yi, yi - .03 * pad],
                color=C_INK, lw=.9, clip_on=False)
        ax.text(1.55, yi + .02 * pad, f'group × session P = {pi:.3f}',
                ha='center', va='bottom', fontsize=6.4, color=C_INK,
                fontweight='bold' if pi > .95 else 'normal', clip_on=False)
        ax.set_ylim(bot - .08 * pad, top + .50 * pad)
        ax.set_xlim(-.55, 3.65)
        ax.set_xticks([x for *_, x in CELLS])
        ax.set_xticklabels(['C', 'S', 'C', 'S'])
        ax.text(0.425, -.20, 'Session 1', transform=ax.get_xaxis_transform(),
                ha='center', va='top', fontsize=6.6, color='0.35')
        ax.text(2.675, -.20, 'Session 2', transform=ax.get_xaxis_transform(),
                ha='center', va='top', fontsize=6.6, color='0.35')
        ax.set_title(LABEL[par], fontsize=8, pad=26)
        ax.set_ylabel(UNITS[par])
    fig.text(.5, -.045, 'C = control, S = stress.  Pale = session 1, solid = session 2.  '
             'Baseline P = posterior probability of a group difference at session 1.  '
             'Group × session P = posterior probability of the interaction, the effect '
             'the paper reports.  '
             'Dotted line, the objective value in the task.',
             fontsize=6.4, color='0.4', ha='center')
    sns.despine(fig=fig, offset=3)
    save(fig, 'fig_group_parameters')


# ------------------------------------------------------------------ figure 5
def choice_figure():
    """Raw choice proportions - no model, no reconstruction."""
    from common import get_behavior
    b = get_behavior().dropna(subset=['chose_risky']).copy()
    b['x'] = np.log(b.n_risky / b.n_safe)
    COL = {0: C_SAFE, 1: C_RISKY}
    NAME = {0: 'Control', 1: 'Stress'}
    rng = np.random.default_rng(0)

    fig, axes = plt.subplots(1, 3, figsize=(7.25, 2.5), constrained_layout=True,
                             gridspec_kw=dict(width_ratios=[1, 1.25, 1.1]))

    # (a) per-participant proportions, both sessions
    ax = axes[0]
    s = b.groupby(['subject', 'group', 'session']).chose_risky.mean().unstack('session')
    for g in (0, 1):
        d = s.xs(g, level='group')
        for j, ses in enumerate([1, 2]):
            xpos = g * 2.6 + j
            ax.plot(rng.normal(xpos, .06, len(d)), d[ses], 'o', color=COL[g], ms=2.8,
                    alpha=.35, mew=0)
            m, se_ = d[ses].mean(), d[ses].std(ddof=1) / np.sqrt(len(d))
            ax.plot([xpos - .26, xpos + .26], [m, m], color=COL[g], lw=2.2)
            ax.plot([xpos, xpos], [m - se_, m + se_], color=COL[g], lw=1.4)
        for i in range(len(d)):
            ax.plot([g * 2.6, g * 2.6 + 1], d.iloc[i].values, color='0.8', lw=.35, zorder=0)
    ax.axhline(.5, color=C_REF, lw=.7, ls='--', zorder=0)
    ax.set_xticks([0, 1, 2.6, 3.6]); ax.set_xticklabels(['1', '2', '1', '2'])
    ax.set_xlabel('Session'); ax.set_ylabel('P(chose risky)')
    ax.set_ylim(.15, .85)
    for g, xc in [(0, .17), (1, .83)]:
        ax.text(xc, 1.02, NAME[g], transform=ax.transAxes, ha='center', va='bottom',
                color=COL[g], fontsize=7.5)

    # (b) psychometric curves
    ax = axes[1]
    b['bin'] = pd.qcut(b.x, 7)
    ctr = b.groupby('bin', observed=True).x.mean()
    for g in (0, 1):
        for ses, ls in [(1, (0, (3.5, 2))), (2, '-')]:
            d = b[(b.group == g) & (b.session == ses)]
            m = d.groupby('bin', observed=True).chose_risky.agg(['mean', 'sem'])
            ax.errorbar(ctr.values, m['mean'], yerr=m['sem'], color=COL[g], ls=ls,
                        lw=1.3 if ses == 2 else 1.0, marker='o', ms=2.6,
                        elinewidth=.8, capsize=0, alpha=.95 if ses == 2 else .7)
    ax.axhline(.5, color=C_REF, lw=.7, ls='--', zorder=0)
    ax.axvline(0, color=C_REF, lw=.7, ls='--', zorder=0)
    ax.set_xlabel('log(risky / safe payoff)'); ax.set_ylabel('P(chose risky)')
    ax.text(.03, .96, 'Dashed: session 1\nSolid: session 2', transform=ax.transAxes,
            ha='left', va='top', fontsize=6.4, color='0.4', linespacing=1.3)

    # (c) session-1 group difference by bin
    ax = axes[2]
    s1 = b[b.session == 1]
    t = s1.groupby(['bin', 'group'], observed=True).chose_risky.mean().unstack()
    n = s1.groupby(['bin', 'group'], observed=True).chose_risky.agg('sem').unstack()
    diff = t[1] - t[0]
    err = np.sqrt(n[1] ** 2 + n[0] ** 2)
    ax.axhline(0, color=C_REF, lw=.8, ls='--', zorder=0)
    ax.errorbar(ctr.values, diff.values, yerr=err.values, color=C_INK, lw=1.2,
                marker='o', ms=3, elinewidth=.8, capsize=0)
    ax.axhline(diff.mean(), color=C_RISKY, lw=1.0, ls=':')
    ax.text(ctr.values[-1], diff.mean() + .012, f'mean {diff.mean():+.3f}', color=C_RISKY,
            fontsize=6.4, ha='right', va='bottom')
    ax.set_xlabel('log(risky / safe payoff)')
    ax.set_ylabel('Session-1 difference\n(stress − control)')
    sns.despine(fig=fig, offset=4)
    save(fig, 'fig_choice_proportions')




# ------------------------------------------------------------------ figure 6
def psychometric_figure():
    """Psychophysical curves by group and session.

    No alignment or correction is needed: the design is identical for every
    participant (safe payoff is always one of 7, 10, 14, 20, 28 coins), so the
    pooled curve is well behaved. (An earlier version of this analysis appeared
    flat and non-monotonic because '*_events.tsv' also globs '*_value_events.tsv',
    which carries model-derived percepts rather than presented payoffs.)
    """
    from scipy.optimize import curve_fit
    from scipy.stats import norm
    from common import get_behavior

    b = get_behavior().dropna(subset=['chose_risky']).copy()
    b['x'] = np.log(b.n_risky / b.n_safe)
    edges = np.quantile(b.x, np.linspace(0, 1, 9))
    b['bin'] = pd.cut(b.x, edges, include_lowest=True)
    centres = b.groupby('bin', observed=True).x.mean().values
    COL = {0: C_SAFE, 1: C_RISKY}

    fig, ax = plt.subplots(figsize=(4.0, 3.2), constrained_layout=True)
    xs = np.linspace(edges[0], edges[-1], 200)
    ax.axhline(.5, color=C_REF, lw=.7, ls='--', zorder=0)
    for g in (0, 1):
        for ses, ls, alpha in [(1, (0, (3.5, 2)), .5), (2, '-', 1.)]:
            d = b[(b.group == g) & (b.session == ses)]
            per = d.groupby(['subject', 'bin'], observed=True).chose_risky.mean().unstack()
            m, sem = per.mean(), per.sem()
            ax.errorbar(centres, m.values, yerr=sem.values, fmt='o', ms=3, color=COL[g],
                        alpha=alpha, elinewidth=.8, capsize=0, lw=0, zorder=3)
            popt, _ = curve_fit(lambda x, a_, bb: norm.cdf(a_ + bb * x), centres,
                                m.values, p0=[-1.5, 2], maxfev=20000)
            ax.plot(xs, norm.cdf(popt[0] + popt[1] * xs), color=COL[g], ls=ls, lw=1.5,
                    alpha=alpha, zorder=2)
            x50 = -popt[0] / popt[1]
            ax.plot([x50, x50], [.02, .09], color=COL[g], lw=1.8, alpha=alpha)
    ax.set_xlabel('log(risky / safe payoff)')
    ax.set_ylabel('P(chose risky)')
    ax.set_ylim(0, 1)
    ax.text(.03, .97, 'Control', transform=ax.transAxes, color=C_SAFE, fontsize=7.5,
            ha='left', va='top')
    ax.text(.03, .89, 'Stress', transform=ax.transAxes, color=C_RISKY, fontsize=7.5,
            ha='left', va='top')
    ax.text(.03, .78, 'Dashed: session 1\nSolid: session 2\nTicks: indifference',
            transform=ax.transAxes, ha='left', va='top', fontsize=6.3, color='0.4',
            linespacing=1.35)
    sns.despine(fig=fig, offset=4)
    save(fig, 'fig_psychometric')


# ------------------------------------------------------------------ figure 7
def prior_vs_objective_figure():
    """Fitted priors against the payoff distributions they are priors over.

    The objective risky and safe payoff distributions differ by a factor of two
    (mean log 3.353 vs 2.643), but the fitted priors are far more alike than that
    (difference 0.089, 95% CrI [-0.423, +0.469]; P(smaller than objective) = 1.00).
    The risky prior is roughly calibrated; the safe prior is much too optimistic.
    """
    from common import get_behavior
    P = PMCParams()
    b = get_behavior()
    obj = {'risky': np.log(b.n_risky.values), 'safe': np.log(b.n_safe.values)}
    COL = {'risky': C_RISKY, 'safe': C_SAFE}

    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.7), sharex=True, constrained_layout=True)
    xs = np.linspace(np.log(3.5), np.log(130), 400)
    for ax, (gname, g) in zip(axes, [('Control', 0), ('Stress', 1)]):
        for opt in ('risky', 'safe'):
            ax.hist(obj[opt], bins=40, density=True, color=COL[opt], alpha=.16, lw=0)
        for opt, key in [('risky', 'risky_prior_mu'), ('safe', 'safe_prior_mu')]:
            sdk = 'risky_prior_std' if opt == 'risky' else 'safe_prior_std'
            for ses, ls, alpha in [(1, (0, (3.5, 2)), .5), (2, '-', 1.)]:
                mu = (P.draws(key)[:, 0] + P.value('prior_mu', ses, g)).mean()
                sd = softplus(P.value(sdk, ses, g)).mean()
                ax.plot(xs, np.exp(-.5 * ((xs - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi)),
                        color=COL[opt], ls=ls, lw=1.5, alpha=alpha)
        ax.set_title(gname, fontsize=8, pad=5)
        ax.set_xlabel('Payoff (coins)')
        ax.set_xticks(np.log([5, 10, 20, 40, 80]))
        ax.set_xticklabels(['5', '10', '20', '40', '80'])
        ax.set_ylabel('Density' if g == 0 else '')
    axes[0].text(.03, .97, 'Shaded: payoffs actually presented\nLines: fitted priors\n'
                 'Dashed session 1, solid session 2', transform=axes[0].transAxes,
                 ha='left', va='top', fontsize=6.3, color='0.4', linespacing=1.35)
    axes[1].text(.97, .97, 'Risky', transform=axes[1].transAxes, color=C_RISKY,
                 ha='right', va='top', fontsize=7.5)
    axes[1].text(.97, .88, 'Safe', transform=axes[1].transAxes, color=C_SAFE,
                 ha='right', va='top', fontsize=7.5)
    sns.despine(fig=fig, offset=4)
    save(fig, 'fig_prior_vs_objective')


if __name__ == '__main__':
    baseline_figure()
    neural_figure()
    correlation_figure()
    parameter_figure()
    choice_figure()
    psychometric_figure()