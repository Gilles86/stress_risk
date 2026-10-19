"""Power of the group x session design vs a single-session between-group design.

Reviewer 2 (point 3) argues n = 25 per group is too small. This asks whether the
baseline session buys power, using ONLY quantities that do not depend on the
stress effect:

  * test-retest r and between-subject SD of risk attitude, CONTROL group only
  * hypothetical effects of d = 0.4, 0.6, 0.8 between-subject SD (not our result)

Risk attitude = RNP from independent (unpooled) probit fits per subject x session,
    chose_risky ~ 1 + log(risky/safe),  RNP = exp(intercept / slope)
Unpooled because the hierarchical models shrink subjects toward their own group x
session cell, which changes the session-1/session-2 correlation. For comparison
the script also reports r of the paper model's per-subject RNP
(`behavior/subject-session-wise_rnp.tsv`, identical to the per-subject estimates of
bambi-RNP-fit_trace_model-paper) and of plain P(chose risky). Model-5 prior means
are NOT used: model 5 gives each subject one intercept plus a session slope with
session coded 1/2, which by construction implies a high r.

Three analyses of the same two-group study, two-sided alpha = .05, exact power from
the noncentral t (no simulation):

  Single session   two-sample t-test on session 2.        Effect / SD
  Change score     two-sample t-test on session 2 - 1.    Effect / SD_change
                   (= the group x session interaction)
  ANCOVA           session 2 ~ group + session 1.         Effect / (SD sqrt(1 - r^2))

SD is the between-subject SD pooled over the two control sessions. With equal SDs,
SD_change = SD sqrt(2 (1 - r)), so the change score beats a single session only when
r > .5. ANCOVA beats both for every r.

Usage:  python power_within_vs_between.py [--bids_folder /data/ds-stressrisk]
Writes power_within_vs_between.{pdf,png} and power_within_vs_between_summary.txt
next to this script.
"""
import argparse
import os.path as op
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from scipy import stats

REPO = op.dirname(op.dirname(op.abspath(__file__)))
sys.path.insert(0, REPO)  # stress_risk is not pip-installed in every env
from stress_risk.utils.data import get_data  # noqa: E402

ALPHA = .05
N_STUDY = 25
DS = [.4, .6, .8]
NS = np.arange(10, 101)
N_BOOT = 5000
OUT = op.join(op.dirname(op.abspath(__file__)), 'power_within_vs_between')

ANALYSES = ['single_cost', 'single', 'change', 'ancova']
COLORS = {'single_cost': '#2E2E2E', 'single': '#9C9C9C', 'change': '#3B5BA5',
          'ancova': '#5D8C3F'}
STYLES = {'single_cost': '-.', 'single': '--', 'change': '-', 'ancova': '-'}
LABELS = {'single_cost': 'Single session, same scans (2 × n per group)',
          'single': 'Single session, same people (n per group)',
          'change': 'Change score (this study)',
          'ancova': 'ANCOVA on baseline'}


# --------------------------------------------------------------------------- data

def probit_fits(df):
    rows = []
    for (sub, group, ses), d in df.groupby(['subject', 'group', 'session']):
        fit = sm.GLM(d.chose_risky.astype(float), sm.add_constant(d.lr),
                     family=sm.families.Binomial(sm.families.links.Probit())).fit()
        a, b = fit.params['const'], fit.params['lr']
        rows.append(dict(subject=sub, group=group, session=ses,
                         rnp=np.exp(a / b), prisky=d.chose_risky.mean()))
    return pd.DataFrame(rows)


def load(bids_folder):
    df = get_data(bids_folder).reset_index().dropna(subset=['chose_risky'])
    df['lr'] = df['log(risky/safe)']
    fits = probit_fits(df)
    tsv = pd.read_csv(op.join(REPO, 'stress_risk', 'behavior',
                              'subject-session-wise_rnp.tsv'), sep='\t')
    fits = fits.merge(tsv[['subject', 'session', 'rnp']]
                      .rename(columns={'rnp': 'rnp_model'}),
                      on=['subject', 'session'], how='left')
    ctrl = fits[fits.group == 0]
    return {m: ctrl.pivot(index='subject', columns='session', values=m)
            for m in ['rnp', 'rnp_model', 'prisky']}


def describe(w, seed=0):
    """r, SDs and change-score SD of a subject x session table, with bootstrap CIs."""
    def stats_of(x1, x2):
        sd = np.sqrt((x1.var(ddof=1) + x2.var(ddof=1)) / 2)
        sd_change = (x2 - x1).std(ddof=1)
        return np.corrcoef(x1, x2)[0, 1], sd, sd_change / sd

    x1, x2 = w[1].values, w[2].values
    r, sd, ratio = stats_of(x1, x2)
    rng = np.random.default_rng(seed)
    boot = np.array([stats_of(x1[i], x2[i]) for i in
                     (rng.integers(0, len(x1), len(x1)) for _ in range(N_BOOT))])
    lo, hi = np.percentile(boot, [2.5, 97.5], axis=0)
    return dict(n=len(w), r=r, r_ci=(lo[0], hi[0]), sd1=w[1].std(), sd2=w[2].std(),
                sd=sd, sd_change=(x2 - x1).std(ddof=1), ratio=ratio,
                ratio_ci=(lo[2], hi[2]), ratio_theory=np.sqrt(2 * (1 - r)))


# -------------------------------------------------------------------------- power

def power_t(d, n, df):
    ncp = d * np.sqrt(n / 2)
    crit = stats.t.ppf(1 - ALPHA / 2, df)
    return stats.nct.sf(crit, df, ncp) + stats.nct.cdf(-crit, df, ncp)


def power(analysis, d, n, r=None, ratio=None):
    """d in between-subject SD units; ratio = SD_change / SD (default from r)."""
    n = np.asarray(n, float)
    if analysis == 'single':
        return power_t(d, n, 2 * n - 2)
    if analysis == 'change':
        ratio = np.sqrt(2 * (1 - r)) if ratio is None else ratio
        return power_t(d / ratio, n, 2 * n - 2)
    if analysis == 'ancova':
        return power_t(d / np.sqrt(1 - r ** 2), n, 2 * n - 3)


def n_for(analysis, d, target, **kw):
    """Smallest n per group with power >= target."""
    ns = np.arange(4, 2000)
    return int(ns[np.argmax(power(analysis, d, ns, **kw) >= target)])


def matching_n_single(p):
    """n per group a single-session design needs to reach power p (continuous)."""
    ns = np.linspace(4, 400, 20000)
    return lambda d: ns[np.argmax(power('single', d, ns) >= p(d))]


# ------------------------------------------------------------------------- figure

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


def letter(ax, s, x=-.2):
    ax.text(x, 1.06, s, transform=ax.transAxes, fontsize=8, fontweight='bold',
            va='bottom', ha='right')


def annotate(ax, text, xy, xytext, color='.25', **kw):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=6.5, color=color,
                va='center', **kw,
                arrowprops=dict(arrowstyle='-|>', color='.25', lw=1.,
                                mutation_scale=8, shrinkA=2, shrinkB=4))


def p_at(analysis, d, n, est):
    """Power of `analysis` when the two-session study has n per group."""
    if analysis == 'single_cost':
        return power('single', d, 2 * np.asarray(n, float))
    if analysis == 'single':
        return power('single', d, n)
    if analysis == 'change':
        return power('change', d, n, ratio=est['ratio'])
    return power('ancova', d, n, r=est['r'])


def make_figure(w, est, others):
    set_style()
    fig = plt.figure(figsize=(7.25, 5.4), constrained_layout=True)
    gs = fig.add_gridspec(2, 3)
    r, ratio = est['r'], est['ratio']

    # a: test-retest scatter, control group
    ax = fig.add_subplot(gs[0, 0])
    lim = (.15, .9)
    ax.plot(lim, lim, color='.7', lw=.6, ls='--', zorder=0)
    ax.scatter(w[1], w[2], s=14, color=COLORS['change'], edgecolor='w', lw=.4, zorder=3)
    ax.set(xlim=lim, ylim=lim, xticks=[.2, .4, .6, .8], yticks=[.2, .4, .6, .8],
           xlabel='RNP, session 1', ylabel='RNP, session 2', aspect='equal')
    ax.set_title(f'Controls, n = {est["n"]}: r = {r:.2f} '
                 f'[{est["r_ci"][0]:.2f}, {est["r_ci"][1]:.2f}]\n'
                 f'SD = {est["sd"]:.3f}, SD change = {est["sd_change"]:.3f} '
                 f'({ratio:.2f} × SD)', fontsize=6.5, loc='left', color='.2')
    ax.text(.74, .77, 'Identity', rotation=45, color='.5', fontsize=6.5,
            ha='center', va='center', rotation_mode='anchor')
    ax.text(.88, .2, 'Risk attitude is only\nmodestly stable across\nthe two sessions',
            color='.25', fontsize=6.5, ha='right', va='bottom')
    letter(ax, 'a')

    # b: power as a function of r, d = 0.6, this study's 25 + 25
    d_b = .6
    ax = fig.add_subplot(gs[0, 1])
    rs = np.linspace(0, .95, 200)
    lo, hi = est['r_ci']
    ax.plot([lo, hi], [.12, .12], color=COLORS['change'], lw=1., zorder=4)
    ax.plot(r, .12, 'o', color=COLORS['change'], ms=4, zorder=5)
    ax.vlines(r, .12, .78, color=COLORS['change'], lw=.6, zorder=1)
    ax.text(r + .02, .14, f'RNP r = {r:.2f}', color=COLORS['change'],
            fontsize=6.5, va='bottom', ha='left')
    ax.vlines(.5, 0, .88, color='.6', lw=.6, ls=':', zorder=0)
    ax.text(.515, .9, 'Break-even\nr = 0.5', color='.45', fontsize=6.5,
            ha='left', va='bottom')
    curves = {'single_cost': np.full_like(rs, p_at('single_cost', d_b, N_STUDY, est)),
              'single': np.full_like(rs, p_at('single', d_b, N_STUDY, est)),
              'change': power('change', d_b, N_STUDY, r=rs),
              'ancova': power('ancova', d_b, N_STUDY, r=rs)}
    for a, y in curves.items():
        ax.plot(rs, y, color=COLORS[a], ls=STYLES[a], zorder=3)
    p_obs = float(power('change', d_b, N_STUDY, r=r))
    ax.plot(r, p_obs, 'o', color=COLORS['change'], ms=4, zorder=5)
    ax.text(r + .025, p_obs - .03, f'{p_obs:.2f}', color=COLORS['change'],
            fontsize=6.5, ha='left', va='top')
    ax.text(.02, curves['single_cost'][0] + .015, 'Single session, same scans',
            color=COLORS['single_cost'], fontsize=6.5, va='bottom')
    ax.text(.6, curves['single'][0] - .015, 'Single session,\nsame people',
            color=COLORS['single'], fontsize=6.5, va='top')
    ax.text(.02, .29, 'Change score', color=COLORS['change'], fontsize=6.5, va='top')
    ax.text(.7, .62, 'ANCOVA', color=COLORS['ancova'], fontsize=6.5,
            ha='left', va='center')
    ax.text(.22, .70, 'Baseline\ncosts power', color='.25', fontsize=6.5,
            ha='center', va='center')
    for i, (name, (val, mk)) in enumerate(others.items()):
        ax.plot(val, .02, mk, color='.25', ms=4, mfc='w' if mk == 'v' else '.25',
                clip_on=False, zorder=4)
        yy = .37 - i * .075
        ax.plot(.62, yy, mk, transform=ax.transAxes, color='.25', ms=4,
                mfc='w' if mk == 'v' else '.25')
        ax.text(.66, yy, f'{name} ({val:.2f})', transform=ax.transAxes,
                fontsize=6, va='center', color='.25')
    ax.set(xlim=(0, .95), ylim=(0, 1.02), xticks=[0, .25, .5, .75],
           yticks=[0, .2, .4, .6, .8, 1], xlabel='Test-retest r (control group)',
           ylabel='Power, 100 scanning sessions')
    ax.set_title(f'd = {d_b}', loc='right', fontsize=7, color='.3')
    letter(ax, 'b')

    # c: scanning sessions needed for 80% power vs d
    ax = fig.add_subplot(gs[0, 2])
    dgrid = np.linspace(.3, 1.0, 71)
    sessions = {
        'single_cost': lambda d: 2 * n_for('single', d, .8),
        'change': lambda d: 4 * n_for('change', d, .8, ratio=ratio),
        'ancova': lambda d: 4 * n_for('ancova', d, .8, r=r)}
    for a, f in sessions.items():
        ax.plot(dgrid, [f(d) for d in dgrid], color=COLORS[a], ls=STYLES[a])
    ax.axhline(4 * N_STUDY, color='.6', lw=.6, zorder=0)
    ax.text(.31, 4 * N_STUDY * 1.06, 'This study', color='.45', fontsize=6.5,
            ha='left', va='bottom')
    s6 = {a: f(.6) for a, f in sessions.items()}
    annotate(ax, f'Two sessions cost\n{s6["change"] / s6["single_cost"]:.1f}× the scans '
             f'at d = 0.6', xy=(.6, s6['change']), xytext=(.64, 700), ha='left')
    ax.text(.72, 48, 'Single session', color=COLORS['single_cost'], fontsize=6.5,
            ha='center', va='top')
    ax.set(yscale='log', xlim=(.3, 1.0), ylim=(25, 1000), xticks=[.3, .4, .6, .8, 1.0],
           xlabel='Effect size d (between-subject SD)',
           ylabel='Scanning sessions for 80% power')
    ax.set_yticks([25, 50, 100, 250, 500, 1000])
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f'{v:g}'))
    ax.yaxis.set_minor_formatter(mpl.ticker.NullFormatter())
    letter(ax, 'c')

    # d-f: power vs n per group of the two-session design, one panel per d
    axes = [fig.add_subplot(gs[1, i]) for i in range(3)]
    rlo, rhi = est['ratio_ci']
    for ax, d in zip(axes, DS):
        ax.axhline(.8, color='.6', lw=.6, ls=':', zorder=0)
        ax.axvline(N_STUDY, color='.6', lw=.6, zorder=0)
        ax.fill_between(NS, power('change', d, NS, ratio=rhi),
                        power('change', d, NS, ratio=rlo),
                        color=COLORS['change'], alpha=.1, lw=0, zorder=1)
        for a in ANALYSES:
            ax.plot(NS, p_at(a, d, NS, est), color=COLORS[a], ls=STYLES[a], zorder=3)
        for i, a in enumerate(ANALYSES):
            ax.text(N_STUDY + 8, .01 + .07 * (3 - i), f'{float(p_at(a, d, N_STUDY, est)):.2f}',
                    color=COLORS[a], fontsize=6.5, va='bottom')
        ax.set(xlim=(10, 100), ylim=(0, 1.02), xticks=[10, 25, 50, 75, 100],
               yticks=[0, .2, .4, .6, .8, 1],
               xlabel='n per group (25 = this study)')
        ax.set_title(f'd = {d}', loc='right', fontsize=7, color='.3')
    axes[0].set_ylabel('Power')
    axes[-1].text(100, .81, '80%', color='.45', fontsize=6.5, ha='right', va='bottom')
    p_e = float(p_at('change', .6, N_STUDY, est))
    n_e = matching_n_single(lambda _: p_e)(.6)
    axes[1].plot([n_e, N_STUDY], [p_e, p_e], color='.25', lw=.8, zorder=4)
    annotate(axes[1], f'Same power with only\n{n_e:.0f} people per group,\none session each',
             xy=((n_e + N_STUDY) / 2, p_e - .01), xytext=(50, .30), ha='left')
    axes[2].text(98, .45, f'At this budget, one\nsession reaches '
                 f'{float(p_at("single_cost", .8, N_STUDY, est)):.0%}',
                 color='.25', fontsize=6.5, ha='right', va='center')
    for ax, s_ in zip(axes, 'def'):
        letter(ax, s_)

    handles = [mpl.lines.Line2D([], [], color=COLORS[a], ls=STYLES[a], label=LABELS[a])
               for a in ANALYSES]
    handles.append(mpl.patches.Patch(color=COLORS['change'], alpha=.1, lw=0,
                                     label='Change score across r 95% CI'))
    leg = fig.legend(handles=handles, loc='outside lower center', ncol=3,
                     frameon=False, fontsize=6.5, handlelength=2.6)
    for t, h in zip(leg.get_texts(), handles):
        t.set_color(h.get_facecolor() if isinstance(h, mpl.patches.Patch)
                    else h.get_color())
    leg.get_texts()[-1].set_color(COLORS['change'])

    sns.despine(fig=fig, offset=4, trim=True)
    fig.savefig(OUT + '.pdf')
    fig.savefig(OUT + '.png')
    return fig


# ------------------------------------------------------------------------ summary

def summary(est, alt):
    r, ratio = est['r'], est['ratio']
    lines = [
        'Control group (n = %d), RNP from unpooled per-session probit fits' % est['n'],
        f'  test-retest r = {r:.3f}, bootstrap 95% CI [{est["r_ci"][0]:.3f}, '
        f'{est["r_ci"][1]:.3f}]',
        f'  between-subject SD: session 1 = {est["sd1"]:.4f}, session 2 = '
        f'{est["sd2"]:.4f}, pooled = {est["sd"]:.4f}',
        f'  SD of change scores = {est["sd_change"]:.4f} = {ratio:.3f} x SD '
        f'(95% CI [{est["ratio_ci"][0]:.3f}, {est["ratio_ci"][1]:.3f}]); '
        f'theory sqrt(2(1-r)) = {est["ratio_theory"]:.3f}',
        '',
        'Other measures of risk attitude, control group:',
    ]
    for name, e in alt.items():
        lines.append(f'  {name:32s} r = {e["r"]:.2f} [{e["r_ci"][0]:.2f}, '
                     f'{e["r_ci"][1]:.2f}], SD_change/SD = {e["ratio"]:.2f}')
    lines += ['', f'Power with this study\'s budget, {N_STUDY} per group x 2 sessions '
              f'= {4 * N_STUDY} scans (two-sided alpha = .05):',
              f'  {"d":>4s}  {"1 ses, 50/grp":>13s}  {"1 ses, 25/grp":>13s}  '
              f'{"change":>7s}  {"ANCOVA":>7s}  single-session n/group matching '
              f'change / ANCOVA']
    for d in DS:
        p = {a: float(p_at(a, d, N_STUDY, est)) for a in ANALYSES}
        m_change = matching_n_single(lambda _: p['change'])(d)
        m_ancova = matching_n_single(lambda _: p['ancova'])(d)
        lines.append(f'  {d:4.1f}  {p["single_cost"]:13.2f}  {p["single"]:13.2f}  '
                     f'{p["change"]:7.2f}  {p["ancova"]:7.2f}  '
                     f'{m_change:.0f} / {m_ancova:.0f}')
    lines += ['', 'For 80% power, n per group (scanning sessions in total):']
    for d in DS:
        ns, nc, na = (n_for('single', d, .8), n_for('change', d, .8, ratio=ratio),
                      n_for('ancova', d, .8, r=r))
        lines.append(f'  d = {d}: single session {ns} ({2 * ns}), change score '
                     f'{nc} ({4 * nc}), ANCOVA {na} ({4 * na})')
    lines += ['', 'Break-even: at equal n per group the change score beats a single '
              'session only if r > 0.5.',
              'At equal scanning cost it needs SD_change < SD / sqrt(2), i.e. r > 0.75.']
    return '\n'.join(lines)


def main(bids_folder):
    w = load(bids_folder)
    est = describe(w['rnp'])
    alt = {'RNP, paper hierarchical model': describe(w['rnp_model']),
           'P(chose risky)': describe(w['prisky'])}
    others = {'Hierarchical-model RNP': (alt['RNP, paper hierarchical model']['r'], 'v'),
              'P(chose risky)': (alt['P(chose risky)']['r'], 'o')}
    make_figure(w['rnp'], est, others)
    text = summary(est, alt)
    with open(OUT + '_summary.txt', 'w') as f:
        f.write(text + '\n')
    print(text)
    print(f'\nWrote {OUT}.pdf/.png and {OUT}_summary.txt')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bids_folder', default='/data/ds-stressrisk')
    main(parser.parse_args().bids_folder)
