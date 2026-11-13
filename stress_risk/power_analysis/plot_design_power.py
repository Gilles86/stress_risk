"""Power of the three candidate designs from the June 2022 design discussion.

Re-draws the simulation in `func_power.m` / `test_SD.m` (Gökhan) and Gilles's
Python rerun (`notes/plots_220616.png`), but with exact power from the
noncentral t instead of 1000 Monte-Carlo draws, so the curves are smooth.

Scores are standard normal (between-subject SD = 1), so the effect is in
between-subject SD units; rho is the session-1/session-2 correlation.
Two ways to put the designs side by side (one figure each):

  participants  same number of people in every design (N on the x-axis)
  sessions      same number of scanning sessions, i.e. the same cost. Between
                groups then gets twice as many people, because each is scanned
                once. This is the comparison that decided the design.

N is the TOTAL number of participants:

  Between  two groups of N/2, two-sample t-test on session 2 only
  Mixed    two groups of N/2, everyone does a baseline session, two-sample
           t-test on the session-2 minus session-1 change. This is the design
           that was run; with two sessions it is the group x session test.
  Within   all N do both conditions, paired t-test

The same-cost figure also marks the measured session-1/session-2 correlation of
RNP and of choice consistency, from plain per-subject, per-session probit fits
(chose_risky ~ 1 + log(risky/safe); RNP = exp(intercept / slope), consistency
= slope), centred within group so the stress effect does not enter it.
Subjects with a degenerate fit (slope <= 0.05 in either session: 49 and 54)
are dropped. Model-5 subject estimates are NOT used for this: model 5 gives
each subject one intercept plus an independent session slope with session
coded 1/2, which by itself implies rho ~0.9 for any data.

Usage:  python plot_design_power.py [--check] [--bids_folder /data/ds-stressrisk]
        (writes design_power_{participants,sessions,same_cost}.pdf/.png next to it)
"""
import argparse
import os.path as op

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from scipy import stats

ALPHA = .05
N_STUDY = 50
RHOS = [.25, .5, .85]
EFFECTS = [.3, .5, .7]
SESSIONS_PER_PERSON = {'Between': 1, 'Mixed': 2, 'Within': 2}
X_AXIS = {
    # x values, ticks, value for this study, axis label
    'participants': (np.arange(20, 101, 2), [20, 40, 60, 80, 100], N_STUDY,
                     'Participants (total)'),
    'sessions': (np.arange(40, 201, 4), [40, 80, 120, 160, 200], 2 * N_STUDY,
                 'Scanning sessions (total)'),
}

COLORS = {'Between': '#9C9C9C', 'Mixed': '#3B5BA5', 'Within': '#5D8C3F'}
LABELS = {'Between': 'Between groups',
          'Mixed': 'Mixed (this study)',
          'Within': 'Within subject'}


def power_two_sample(d, n_per_group):
    df = 2 * n_per_group - 2
    ncp = d * np.sqrt(n_per_group / 2)
    crit = stats.t.ppf(1 - ALPHA / 2, df)
    return stats.nct.sf(crit, df, ncp) + stats.nct.cdf(-crit, df, ncp)


def power_paired(d, n):
    df = n - 1
    ncp = d * np.sqrt(n)
    crit = stats.t.ppf(1 - ALPHA / 2, df)
    return stats.nct.sf(crit, df, ncp) + stats.nct.cdf(-crit, df, ncp)


def design_power(design, effect, rho, n_total):
    sd_change = np.sqrt(2 * (1 - rho))     # SD of a session-2 minus session-1 score
    if design == 'Between':
        return power_two_sample(effect, n_total / 2)
    if design == 'Mixed':
        return power_two_sample(effect / sd_change, n_total / 2)
    if design == 'Within':
        return power_paired(effect / sd_change, n_total)


def power_at(design, effect, rho, x, per):
    n_total = x if per == 'participants' else x / SESSIONS_PER_PERSON[design]
    return design_power(design, effect, rho, n_total)


def check_against_simulation(n_sims=20000, seed=0):
    """Monte-Carlo replica of func_power.m at one grid point, as a sanity check."""
    rng = np.random.default_rng(seed)
    rho, effect, n = .5, .5, N_STUDY // 2
    cov = [[1, rho], [rho, 1]]
    hits = {'Between': 0, 'Mixed': 0}
    for _ in range(n_sims):
        s = rng.multivariate_normal([0, 0], cov, n)
        c = rng.multivariate_normal([0, 0], cov, n)
        s[:, 1] += effect
        hits['Between'] += stats.ttest_ind(s[:, 1], c[:, 1]).pvalue < ALPHA
        hits['Mixed'] += stats.ttest_ind(s[:, 1] - s[:, 0],
                                         c[:, 1] - c[:, 0]).pvalue < ALPHA
    for k, v in hits.items():
        print(f'{k:8s} simulated {v / n_sims:.3f}  '
              f'exact {design_power(k, effect, rho, N_STUDY):.3f}')


def observed_rho(bids_folder, n_boot=5000, seed=0):
    """Test-retest r of P(risky) per subject, centred within group, + bootstrap CI.

    Also returns split-half (odd/even trial, Spearman-Brown) reliability per
    session, to show the low r is not measurement noise.
    """
    df = pd.read_csv(op.join(bids_folder, 'interim_sum_data', 'all_behavior_df.csv'))
    df = df.dropna(subset=['chose_risky'])
    df['half'] = df.groupby(['subject', 'session']).cumcount() % 2

    def centre(x):
        return x - x.groupby(level='group').transform('mean')

    w = centre(df.groupby(['subject', 'group', 'session']).chose_risky.mean()
               .unstack('session'))
    h = centre(df.groupby(['subject', 'group', 'session', 'half']).chose_risky.mean()
               .unstack(['session', 'half']))

    r = np.corrcoef(w[1], w[2])[0, 1]
    rng = np.random.default_rng(seed)
    boot = [np.corrcoef(*w.iloc[rng.integers(0, len(w), len(w))][[1, 2]].values.T)[0, 1]
            for _ in range(n_boot)]
    split = {ses: np.corrcoef(h[(ses, 0)], h[(ses, 1)])[0, 1] for ses in (1, 2)}
    reliability = {ses: 2 * v / (1 + v) for ses, v in split.items()}
    return r, np.percentile(boot, [2.5, 97.5]), reliability


def probit_rho(bids_folder, min_slope=.05):
    """Test-retest r of probit RNP and slope, centred within group, Fisher-z 95% CI."""
    df = pd.read_csv(op.join(bids_folder, 'interim_sum_data', 'all_behavior_df.csv'))
    df = df.dropna(subset=['chose_risky'])
    df['lr'] = np.log(df.n_risky / df.n_safe)

    rows = []
    for (sub, group, ses), d in df.groupby(['subject', 'group', 'session']):
        fit = sm.GLM(d.chose_risky.astype(float), sm.add_constant(d.lr),
                     family=sm.families.Binomial(sm.families.links.Probit())).fit()
        a, b = fit.params['const'], fit.params['lr']
        rows.append(dict(subject=sub, group=group, session=ses,
                         rnp=np.exp(a / b), slope=b))
    fits = pd.DataFrame(rows)
    bad = fits.loc[fits.slope <= min_slope, 'subject'].unique()
    fits = fits[~fits.subject.isin(bad)]

    out = {}
    for par in ['rnp', 'slope']:
        w = fits.pivot_table(index=['subject', 'group'], columns='session', values=par)
        w = w - w.groupby(level='group').transform('mean')
        r = np.corrcoef(w[1], w[2])[0, 1]
        ci = np.tanh(np.arctanh(r) + np.array([-1, 1]) * 1.96 / np.sqrt(len(w) - 3))
        out[par] = (r, ci, len(w))
    return out, bad


def set_style():
    mpl.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Helvetica', 'Helvetica Neue', 'TeX Gyre Heros', 'Arial'],
        'font.size': 7, 'axes.labelsize': 8, 'axes.titlesize': 8,
        'xtick.labelsize': 7, 'ytick.labelsize': 7,
        'axes.linewidth': .8, 'axes.spines.top': False, 'axes.spines.right': False,
        'xtick.direction': 'out', 'ytick.direction': 'out',
        'xtick.major.size': 3, 'ytick.major.size': 3,
        'xtick.major.width': .8, 'ytick.major.width': .8,
        'lines.linewidth': 1.4,
        'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
        'savefig.dpi': 300, 'savefig.bbox': 'tight', 'savefig.pad_inches': .02,
    })


def main(per):
    xs, xticks, x_study, xlabel = X_AXIS[per]
    dx = xs[-1] - xs[0]
    set_style()
    fig, axes = plt.subplots(len(EFFECTS), len(RHOS), figsize=(7.25, 5.4),
                             sharex=True, sharey=True, constrained_layout=True)

    for i, effect in enumerate(EFFECTS):
        for j, rho in enumerate(RHOS):
            ax = axes[i, j]
            ax.axhline(.8, color='.7', lw=.6, ls='--', zorder=0)
            ax.axvline(x_study, color='.7', lw=.6, ls=':', zorder=0)
            for design in ['Between', 'Within', 'Mixed']:
                p = power_at(design, effect, rho, xs, per)
                ax.plot(xs, p, color=COLORS[design],
                        lw=2. if design == 'Mixed' else 1.2,
                        zorder=3 if design == 'Mixed' else 2)
            p_study = power_at('Mixed', effect, rho, x_study, per)
            ax.plot(x_study, p_study, 'o', ms=4, color=COLORS['Mixed'], zorder=4)
            ax.text(x_study + .025 * dx, p_study - .02, f'{p_study:.2f}',
                    color=COLORS['Mixed'], fontsize=6.5, va='top')

            if i == 0:
                ax.set_title(f'Test-retest ρ = {rho}')
            if j == 0:
                ax.set_ylabel(f'Effect = {effect} SD\nPower')

    for ax in axes[-1]:
        ax.set_xlabel(xlabel)
    axes[0, 0].set_xticks(xticks)
    axes[0, 0].set_yticks([0, .2, .4, .6, .8, 1])
    axes[0, 0].set_ylim(0, 1.02)

    # Direct labels in one panel; colour carries them to the rest
    ax = axes[0, 0]
    for k, (design, y) in enumerate([('Within', .985), ('Between', .925), ('Mixed', .865)]):
        ax.plot([.05, .13], [y, y], transform=ax.transAxes, color=COLORS[design],
                lw=2. if design == 'Mixed' else 1.2, solid_capstyle='butt')
        ax.text(.16, y, LABELS[design], transform=ax.transAxes,
                color=COLORS[design], fontsize=6.5, va='center')
    axes[0, 1].text(x_study + .02 * dx, .97,
                    'This study' if per == 'sessions' else 'N = 50',
                    color='.45', fontsize=6.5, va='top', ha='left')
    if per == 'participants':
        axes[0, 1].text(76, .30, 'Between groups = mixed\nwhen ρ = 0.5', color='.45',
                        fontsize=6.5, va='bottom', ha='center')
    axes[0, 2].text(xs[-1] - .01 * dx, .82, '80%', color='.45', fontsize=6.5, va='bottom', ha='right')

    sns.despine(fig=fig, offset=4, trim=True)

    out = op.join(op.dirname(op.abspath(__file__)), f'design_power_{per}')
    fig.savefig(out + '.pdf')
    fig.savefig(out + '.png')
    print(f'Wrote {out}.pdf/.png')


MEASURES = {'rnp': ('RNP', '#C44E52'), 'slope': ('Consistency', '#8172B2')}


def main_same_cost(measured):
    """The three designs at this study's cost (100 sessions), against rho.

    Between: 50 stressed + 50 controls, scanned once.
    Mixed:   25 + 25, each scanned at baseline and after the manipulation.
    Within:  50 people, each scanned once stressed and once not (no order effects).
    """
    set_style()
    sessions = 2 * N_STUDY
    rhos = np.linspace(0, .95, 96)
    fig, axes = plt.subplots(1, len(EFFECTS), figsize=(7.25, 2.4),
                             sharey=True, constrained_layout=True)
    for ax, effect in zip(axes, EFFECTS):
        ax.axhline(.8, color='.7', lw=.6, ls='--', zorder=0)
        ax.vlines(.75, .35, 1.02, color='.7', lw=.6, ls=':', zorder=0)  # mixed = between
        for par, (r, ci, n) in measured.items():
            ax.axvline(r, color=MEASURES[par][1], lw=1., zorder=1)
        p_between = power_at('Between', effect, 0, sessions, 'sessions')
        p_mixed = power_at('Mixed', effect, rhos, sessions, 'sessions')
        ax.plot(rhos, np.full_like(rhos, p_between), color=COLORS['Between'], lw=1.2)
        ax.plot(rhos, power_at('Within', effect, rhos, sessions, 'sessions'),
                color=COLORS['Within'], lw=1.2)
        ax.plot(rhos, p_mixed, color=COLORS['Mixed'], lw=2.)
        for par, (r, ci, n) in measured.items():
            for design in ['Within', 'Mixed']:
                ax.plot(r, power_at(design, effect, r, sessions, 'sessions'), 'o',
                        ms=3.5, color=COLORS[design], zorder=4)
        ax.text(.94, p_between - .02, f'{p_between:.2f}', color='.45',
                fontsize=6.5, va='top', ha='right')
        ax.set_title(f'Effect = {effect} SD')
        ax.set_xlabel('Test-retest ρ')
        ax.set_xticks([0, .25, .5, .75, .95])
    axes[0].set_ylabel('Power')
    axes[0].set_yticks([0, .2, .4, .6, .8, 1])
    axes[0].set_ylim(0, 1.02)

    ax = axes[2]
    for design, label, y in [('Within', '50, both conds.', .31),
                             ('Between', '50 + 50, one ses.', .24),
                             ('Mixed', '25 + 25, two ses.', .17)]:
        ax.plot([.58, .65], [y, y], transform=ax.transAxes, color=COLORS[design],
                lw=2. if design == 'Mixed' else 1.2, solid_capstyle='butt')
        ax.text(.67, y, label, transform=ax.transAxes, color=COLORS[design],
                fontsize=6.5, va='center')
    (r_rnp, _, _), (r_slope, _, _) = measured['rnp'], measured['slope']
    axes[1].text(r_rnp - .02, .03, f'RNP\nρ = {r_rnp:.2f}', color=MEASURES['rnp'][1],
                 fontsize=6.5, ha='right', va='bottom')
    axes[1].text(r_slope + .02, .03, f'Consistency\nρ = {r_slope:.2f}',
                 color=MEASURES['slope'][1], fontsize=6.5, ha='left', va='bottom')

    axes[2].text(.94, .78, '80%', color='.45', fontsize=6.5, va='top', ha='right')

    sns.despine(fig=fig, offset=4, trim=True)
    out = op.join(op.dirname(op.abspath(__file__)), 'design_power_same_cost')
    fig.savefig(out + '.pdf')
    fig.savefig(out + '.png')
    print(f'Wrote {out}.pdf/.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--bids_folder', default='/data/ds-stressrisk')
    args = parser.parse_args()
    if args.check:
        check_against_simulation()

    rho_obs, rho_ci, reliability = observed_rho(args.bids_folder)
    print(f'Test-retest r of P(risky), within group: {rho_obs:.2f} '
          f'[{rho_ci[0]:.2f}, {rho_ci[1]:.2f}]; split-half reliability '
          f'ses-1 {reliability[1]:.2f}, ses-2 {reliability[2]:.2f}')
    measured, dropped = probit_rho(args.bids_folder)
    print(f'Probit fits, dropped subjects {list(dropped)}')
    for par, (r, ci, n) in measured.items():
        print(f'Test-retest r of {par}: {r:.2f} [{ci[0]:.2f}, {ci[1]:.2f}], n = {n}; '
              + ', '.join(f'{d} {power_at(d, .5, r, 2 * N_STUDY, "sessions"):.2f}'
                          for d in ['Between', 'Mixed', 'Within'])
              + ' (power at 0.5 SD, 100 sessions)')
    for per in X_AXIS:
        main(per)
    main_same_cost(measured)
