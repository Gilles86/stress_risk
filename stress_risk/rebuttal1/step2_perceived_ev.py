"""R1.1 + R1 minor e: perceived expected value as a function of objective EV.

NB: the standalone figure this writes (fig3_perceivedEV*.pdf) is superseded by
fig4_mechanism.py, which draws the same curves as its panel D. What is still used
from here is `curves()` (imported by fig4_mechanism) and the printed risky/safe
ratio at matched objective EV.

Reviewer 1 reasoned that because the safe prior is less precise than the risky
prior, an equal shift in both priors moves the *risky* percept more, so a common
prior shift can produce more risk-seeking. This figure shows that directly, and
step 1 confirmed the premise (safe prior ~2x wider, P = .997-1.000).

Panels: presentation order x group; within each, risky/safe option x session.
Two versions: log-log axes (`--space log`), where the Bayesian shrinkage is a
straight line and the distance from the diagonal reads directly as distortion; and
natural axes (`--space natural`), where shrinkage appears as a compressive curve and
the vertical gap between risky and safe is in coins.
"""
import argparse
import os.path as op
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sys.path.insert(0, op.dirname(op.abspath(__file__)))
from common import PMCParams, RISKY_P, perceived_ev, weight  # noqa: E402

OUT = '/Users/gdehol/git/stress_risk/notes/rebuttal1/results'
C_SAFE, C_RISKY, C_REF = '#3B5BA5', '#C44E52', '#B0B0B0'

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
money = mpl.ticker.FuncFormatter(lambda x, _: f'{x:g}')


def curves(P, session, group, risky_first, ev, n_draws=400):
    """Perceived EV of the risky and safe option over a grid of matched objective EVs."""
    c = P.cell(session, group)
    ix = np.random.default_rng(0).choice(len(c['nu1']), n_draws, replace=False)
    # first-presented option carries nu1 (perception + working memory), second nu2
    nu_r, nu_s = (c['nu1'], c['nu2']) if risky_first else (c['nu2'], c['nu1'])
    out = {}
    out['risky'] = np.stack([perceived_ev(ev / RISKY_P, RISKY_P, c['mu_risky'][i],
                                          c['sd_risky'][i], nu_r[i]) for i in ix])
    out['safe'] = np.stack([perceived_ev(ev, 1.0, c['mu_safe'][i],
                                         c['sd_safe'][i], nu_s[i]) for i in ix])
    return out


def draw_perceived_ev(axes, P, space='log'):
    """Draw the 2x2 perceived-EV grid (rows: presentation order; cols: group) into `axes`."""
    ev = np.geomspace(6, 40, 120) if space == 'log' else np.linspace(5, 40, 120)
    lo_ax = 6 if space == 'log' else 5
    for r, risky_first in enumerate([True, False]):
        for c, (gname, g) in enumerate([('Control', 0), ('Stress', 1)]):
            ax = axes[r, c]
            ax.plot(ev, ev, ls='--', lw=0.7, color=C_REF, zorder=0)
            for session, ls, alpha in [(1, (0, (3.5, 2)), .30), (2, '-', .30)]:
                cur = curves(P, session, g, risky_first, ev)
                for key, col in [('risky', C_RISKY), ('safe', C_SAFE)]:
                    m = np.median(cur[key], 0)
                    lo, hi = np.percentile(cur[key], [2.5, 97.5], axis=0)
                    if session == 2:
                        ax.fill_between(ev, lo, hi, color=col, alpha=.13, lw=0, zorder=1)
                    ax.plot(ev, m, color=col, ls=ls, lw=1.5 if session == 2 else 1.1,
                            zorder=3 if session == 2 else 2)
            if space == 'log':
                ax.set_xscale('log'); ax.set_yscale('log')
                ticks = [10, 20, 40]
            else:
                ticks = [10, 20, 30, 40]
            ax.set_xlim(lo_ax, 40); ax.set_ylim(lo_ax, 40)
            ax.set_xticks(ticks); ax.set_yticks(ticks)
            ax.xaxis.set_major_formatter(money); ax.yaxis.set_major_formatter(money)
            ax.xaxis.set_minor_locator(mpl.ticker.NullLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.NullLocator())
            if r == 0:
                ax.set_title(gname, pad=6)
            if c == 0:
                ax.set_ylabel('Risky first\n\nPerceived value (coins)' if r == 0
                              else 'Safe first\n\nPerceived value (coins)')
            if r == 1:
                ax.set_xlabel('Objective expected value (coins)')

    # annotation anchors, in data coordinates of each axis type
    if space == 'log':
        leg_x, leg_y, vx, vy = 6.6, (34, 27.5, 22.3), (39, 6.4), None
        arrow_xy, arrow_text = (8.0, 12.4), (13.5, 7.6)
    else:
        leg_x, leg_y, vx, vy = 6.0, (40, 35.2, 30.4), (39, 5.8), None
        arrow_xy, arrow_text = (32.5, 27.6), (21.5, 10.5)
    ax = axes[0, 0]
    ax.text(leg_x, leg_y[0], 'Risky', color=C_RISKY, ha='left', va='top', fontsize=7.5)
    ax.text(leg_x, leg_y[1], 'Safe', color=C_SAFE, ha='left', va='top', fontsize=7.5)
    ax.text(leg_x, leg_y[2], 'Dashed: session 1\nSolid: session 2', color='0.35',
            ha='left', va='top', fontsize=6.5, linespacing=1.35)
    axes[1, 1].text(*vx, 'Veridical', color='0.55', ha='right', va='bottom', fontsize=6.5)
    axes[0, 1].annotate('Under stress, the risky option\nis perceived as more valuable;\nthe safe option is largely unaffected',
        xy=arrow_xy, xytext=arrow_text, fontsize=6.5, ha='left', va='center',
        linespacing=1.35, color='0.25',
        arrowprops=dict(arrowstyle='-|>', color='0.4', lw=.9, mutation_scale=7,
                        shrinkA=3, shrinkB=5, relpos=(0., .5)))


def main(space='log'):
    P = PMCParams()
    suffix = '' if space == 'log' else '_natural'
    fig, axes = plt.subplots(2, 2, figsize=(5.6, 3.9), sharex=True, sharey=True,
                             constrained_layout=True)
    draw_perceived_ev(axes, P, space)

    for ax_, letter in zip(axes.ravel(), 'abcd'):
        ax_.text(-0.12, 1.02, letter, transform=ax_.transAxes, fontsize=8,
                 fontweight='bold', va='bottom', ha='right')
    # NB: trim=True breaks on shared axes (spines detach) - offset only.
    sns.despine(fig=fig, offset=4)
    fig.savefig(op.join(OUT, f'fig3_perceivedEV{suffix}.pdf'), bbox_inches='tight', pad_inches=.02)
    fig.savefig(op.join(OUT, f'fig3_perceivedEV{suffix}.png'), dpi=220, bbox_inches='tight', pad_inches=.02)

    # ---- the quantity the reviewer's argument is really about --------------
    print('Perceived risky/safe value ratio at matched objective EV')
    print('(< 1 = risky looks worse than an EV-matched safe option = apparent risk aversion)\n')
    for gname, g in [('control', 0), ('stress', 1)]:
        for risky_first in (True, False):
            r = {}
            for s in (1, 2):
                cur = curves(P, s, g, risky_first, np.array([10., 20., 30.]))
                r[s] = cur['risky'] / cur['safe']
            d = r[2] - r[1]
            lab = 'risky-first' if risky_first else 'safe-first'
            print(f'  {gname:8s} {lab:11s} '
                  + '  '.join(f'EV={e:.0f}: {r[1][:, i].mean():.3f}->{r[2][:, i].mean():.3f} '
                              f'(d={d[:, i].mean():+.3f}, P(d>0)={np.mean(d[:, i] > 0):.2f})'
                              for i, e in enumerate([10, 20, 30])))
    print(f'\nsaved {OUT}/fig3_perceivedEV{suffix}.pdf')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--space', choices=['log', 'natural'], default='log')
    main(parser.parse_args().space)
