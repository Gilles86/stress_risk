"""New Figure 4 (R1.1): the fitted PMC parameters, and what they imply for value.

Answers R1's question -- how can a prior shift shared by both options make people
more risk-seeking? -- by showing the parameters against the payoffs that were
actually shown (A-C) and the perceived-value curves they produce (D).

  A  Prior mean, per option, in payoff units. Grey band: geometric mean +/-1 SD of
     the payoffs shown for that option; dashed line: their mean.
  B  Prior width sigma, log units. Dashed line: the SD of the log payoffs shown,
     i.e. the value a perfectly calibrated prior would take.
  C  Evidence noise nu, for the first- and second-presented option. No objective
     reference: nu is a property of the observer, not of the stimulus set.
  D  Perceived expected value against objective EV, per presentation order and
     group (natural space; curves from step2_perceived_ev.py).

Style follows the manuscript's Figures 3 and 4: Helvetica Neue, bold upright panel
letter plus bold-italic panel title, italic facet labels, the Figure 3A coolwarm
pair for the risky (warm) and safe (cool) option. Group stays neutral grey -- the
paper's control-blue / stress-orange would fight the risky/safe colours. Session is
carried by marker fill (A-C) and line style (D).

Defaults to model 5, the paper model. `--model 1` runs the same figure on the
parameterisation where the two prior means move separately.

    PYTHONPATH=/Users/gdehol/git/stress_risk python fig4_mechanism.py
"""
import argparse
import os.path as op
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sys.path.insert(0, op.dirname(op.abspath(__file__)))
from common import PMCParams, get_behavior, trace_path  # noqa: E402
from step2_perceived_ev import curves  # noqa: E402

OUT = '/Users/gdehol/git/stress_risk/notes/rebuttal1/results'

_cw = sns.color_palette('coolwarm', 4)[::-1]          # as in Figure 3A
C_RISKY, C_SAFE = _cw[0], _cw[3]
C_GROUP = {'Control': '0.2', 'Stress': '0.2'}
GROUPS = [('Control', 0), ('Stress', 1)]
ORDERS = [(True, 'Risky first'), (False, 'Safe first')]
LS = {1: (0, (3.2, 1.8)), 2: '-'}

FS_TICK, FS_LAB, FS_HEAD = 7.5, 8.5, 9.5
# (parameter, panel title, colour, plot in payoff units)
PARAMS = [('mu_risky', 'Risky', C_RISKY, True), ('mu_safe', 'Safe', C_SAFE, True),
          ('sd_risky', 'Risky', C_RISKY, False), ('sd_safe', 'Safe', C_SAFE, False),
          ('nu1', '1st presented', '0.35', False),
          ('nu2', '2nd presented', '0.35', False)]
LIMS = {'mu': (6.3, 72), 'sd': (0, 1.3), 'nu': (.14, .34)}


def register_helvetica_neue(cache='~/.cache/stress_risk_fonts'):
    """Make Helvetica Neue bold / italic / bold-italic usable in matplotlib.

    macOS ships them inside HelveticaNeue.ttc and matplotlib only indexes the first
    face of a collection, so bold and italic silently fall back to regular. Extract
    faces 0-3 to single .ttf files (local cache only -- Apple fonts, never commit).
    """
    import os
    from matplotlib import font_manager as fm
    cache = op.expanduser(cache)
    os.makedirs(cache, exist_ok=True)
    src = '/System/Library/Fonts/HelveticaNeue.ttc'
    for i in range(4):
        dst = op.join(cache, f'HelveticaNeue-{i}.ttf')
        if not op.exists(dst):
            from fontTools.ttLib import TTCollection
            TTCollection(src).fonts[i].save(dst)
        fm.fontManager.addfont(dst)


register_helvetica_neue()
mpl.rcParams.update({
    'font.family': 'Helvetica Neue', 'font.sans-serif': ['Helvetica Neue', 'Arial'],
    'font.size': FS_TICK, 'axes.labelsize': FS_LAB, 'axes.titlesize': FS_LAB,
    'xtick.labelsize': FS_TICK, 'ytick.labelsize': FS_TICK, 'legend.fontsize': FS_TICK,
    'axes.linewidth': .8, 'axes.edgecolor': '0.15', 'axes.spines.top': False,
    'axes.spines.right': False, 'xtick.major.size': 3, 'ytick.major.size': 3,
    'xtick.major.width': .8, 'ytick.major.width': .8, 'lines.linewidth': 1.3,
    'pdf.fonttype': 42, 'ps.fonttype': 42, 'figure.dpi': 150, 'savefig.dpi': 300,
    # Helvetica's upright Greek nu is all but indistinguishable from a latin "v",
    # so set Greek through mathtext (italic, stix sans -- closest to Helvetica).
    'mathtext.fontset': 'stixsans', 'mathtext.default': 'it',
})


# ----------------------------------------------------------------- pieces -----
def heading(fig, ax, letter, title, dx=0., dy=.012, y=None, fs=FS_HEAD, gap=.027):
    """Figure-3 style heading: bold letter, then bold-italic title, above `ax`."""
    x0 = ax.get_position().x0 + dx
    y = ax.get_position().y1 + dy if y is None else y
    fig.text(x0, y, letter, fontsize=fs, fontweight='bold', va='bottom', ha='left')
    fig.text(x0 + gap, y, title, fontsize=fs, fontweight='bold', style='italic',
             va='bottom', ha='left')


def key(fig, x, y, entries, gap=.020):
    """Inline figure-level key: [(label, kind, kw)], laid out left to right."""
    r = fig.canvas.get_renderer()
    for lab, kind, kw in entries:
        if kind == 'line':
            fig.add_artist(mpl.lines.Line2D([x, x + .026], [y, y], transform=fig.transFigure,
                                            solid_capstyle='butt', **kw))
            x += .032
        elif kind == 'band':
            fig.add_artist(mpl.patches.Rectangle((x, y - .009), .026, .018,
                                                 transform=fig.transFigure, lw=0, **kw))
            x += .032
        else:
            fig.add_artist(mpl.lines.Line2D([x + .006], [y], transform=fig.transFigure,
                                            marker='o', ms=3.4, ls='', mew=.9, **kw))
            x += .016
        t = fig.text(x, y, lab, fontsize=FS_TICK, va='center', color='0.25')
        x += t.get_window_extent(r).width / fig.bbox.width + gap


PARAM_KEY = [('Payoffs shown, ±1 SD', 'band', dict(color='0.90')),
             ('Their mean / SD', 'line', dict(color='0.45', lw=1., ls=(0, (3, 2)))),
             ('Session 1', 'dot', dict(mfc='w', mec='0.35')),
             ('Session 2', 'dot', dict(mfc='0.35', mec='0.35'))]
CURVE_KEY = [('Risky', 'line', dict(color=C_RISKY, lw=1.6)),
             ('Safe', 'line', dict(color=C_SAFE, lw=1.6)),
             ('Session 1', 'line', dict(color='0.35', lw=1.2, ls=LS[1])),
             ('Session 2', 'line', dict(color='0.35', lw=1.2))]


def session_pair(ax, xs, y, col, spans, lw=1.1):
    """One Control-or-Stress row: session 1 above (open), session 2 below (filled)."""
    for s, dy in ((1, .2), (2, -.2)):
        lo, hi = spans[s]
        ax.plot([lo, hi], [y + dy] * 2, color=col, alpha=.45 if s == 1 else 1,
                lw=lw, solid_capstyle='butt', zorder=3)
        ax.plot(xs[s], y + dy, 'o', ms=3.4, zorder=4, mfc='w' if s == 1 else col,
                mec=col, mew=.9)


def dots(ax, par, parameter, col, title='', exp=False, show_groups=True):
    """Posterior mean and 95% CrI for one parameter, Control and Stress rows."""
    f = np.exp if exp else (lambda v: v)
    for (g, _), y in zip(GROUPS, (0., -1.)):
        q = par[(par.group == g) & (par.parameter == parameter)].set_index('session')
        session_pair(ax, {s: f(q.loc[s, 'mean']) for s in (1, 2)}, y, col,
                     {s: (f(q.loc[s, 'lo']), f(q.loc[s, 'hi'])) for s in (1, 2)})
        if show_groups:
            ax.text(-.04, y, g, transform=ax.get_yaxis_transform(), ha='right',
                    va='center', color=C_GROUP[g], style='italic', fontsize=FS_TICK)
    ax.set_yticks([])
    ax.set_ylim(-1.7, .7)
    if title:
        ax.set_title(title, style='italic', pad=3, fontsize=FS_TICK + .5, color=col)


def panel_perceived(axes, P):
    """Four landscape panels: (risky first, safe first) x (control, stress)."""
    ev = np.linspace(5, 40, 100)
    cells = [(rf, g) for rf, _ in ORDERS for g in GROUPS]
    for i, (ax, (rf, (gname, g))) in enumerate(zip(axes, cells)):
        ax.plot(ev, ev, ls=(0, (2, 2)), lw=.7, color='0.6', zorder=0)
        for s in (1, 2):
            cur = curves(P, s, g, rf, ev)
            for which, col in (('risky', C_RISKY), ('safe', C_SAFE)):
                if s == 2:
                    lo, hi = np.percentile(cur[which], [2.5, 97.5], axis=0)
                    ax.fill_between(ev, lo, hi, color=col, alpha=.18, lw=0, zorder=1)
                ax.plot(ev, np.median(cur[which], 0), color=col, ls=LS[s],
                        lw=1.5 if s == 2 else 1.1, zorder=3)
        ax.set_xlim(5, 40); ax.set_ylim(5, 40)
        ax.set_xticks([10, 20, 30, 40]); ax.set_yticks([10, 20, 30, 40])
        ax.text(.04, .97, gname, transform=ax.transAxes, color=C_GROUP[gname],
                style='italic', fontsize=FS_TICK + .5, va='top')
        ax.set_xlabel('Objective\nexpected value', fontsize=FS_TICK, labelpad=2,
                      linespacing=1.15)
        if i:
            ax.tick_params(labelleft=False)


def summarise(P):
    """Posterior mean and 95% CrI of every group-level parameter, per cell."""
    out = []
    for g, gi in GROUPS:
        for s in (1, 2):
            c = P.cell(s, gi)
            for k in ('mu_risky', 'mu_safe', 'sd_risky', 'sd_safe', 'nu1', 'nu2'):
                out.append(dict(group=g, session=s, parameter=k, mean=c[k].mean(),
                                lo=np.percentile(c[k], 2.5), hi=np.percentile(c[k], 97.5)))
    return pd.DataFrame(out)


def log_payoffs():
    """Mean and SD of the log payoffs actually shown, per option: what a perfectly
    calibrated prior would match (mean -> mu, SD -> sigma)."""
    df = get_behavior()
    return {which: (np.log(df[col].astype(float)).mean(),
                    np.log(df[col].astype(float)).std())
            for which, col in (('risky', 'n_risky'), ('safe', 'n_safe'))}


# ------------------------------------------------------------------ figure ----
def build(P, par):
    fig = plt.figure(figsize=(5.7, 4.05))
    shown = log_payoffs()

    # -- A-C: one axis per parameter, objective statistics drawn in behind -----
    g1 = fig.add_gridspec(2, 3, left=.145, right=.985, top=.855, bottom=.565,
                          wspace=.55, hspace=1.05)
    axes = []
    for i, (k, lab, col, exp) in enumerate(PARAMS):
        ax = fig.add_subplot(g1[i % 2, i // 2])
        axes.append(ax)
        fam, which = k.split('_')[0][:2], k.split('_')[-1]
        if fam in ('mu', 'sd'):
            m, sd = shown[which]
            if fam == 'mu':
                ax.axvspan(np.exp(m - sd), np.exp(m + sd), color='0.90', lw=0, zorder=0)
            ax.axvline(np.exp(m) if fam == 'mu' else sd, color='0.45', lw=1.,
                       ls=(0, (3, 2)), zorder=2)
        dots(ax, par, k, col, title=lab, exp=exp, show_groups=(i // 2 == 0))
        ax.set_xlim(*LIMS[fam])
        if fam == 'mu':
            ax.set_xscale('log'); ax.minorticks_off()
            ax.set_xticks([7, 14, 28, 56]); ax.set_xticklabels(['7', '14', '28', '56'])
        elif fam == 'sd':
            ax.set_xticks([0, .5, 1])
        else:
            ax.set_xticks([.15, .25]); ax.set_xticklabels(['.15', '.25'])
        if i % 2:
            ax.set_xlabel('Payoff' if fam == 'mu' else 'Log units', fontsize=FS_TICK)
        sns.despine(ax=ax, left=True, offset=3)

    # Measure where the parameter block really ends, then stack the key and D under
    # it: hard-coded fractions drift onto the x-labels whenever a label changes.
    fig.canvas.draw()
    inv = fig.transFigure.inverted()
    lo = min(inv.transform(ax.xaxis.get_label().get_window_extent(
        fig.canvas.get_renderer()))[0][1] for ax in axes[1::2])
    key_y, head_y = lo - .042, lo - .097

    # -- D: perceived expected value ------------------------------------------
    g2 = fig.add_gridspec(1, 5, width_ratios=[1, 1, .18, 1, 1], left=.145, right=.985,
                          top=head_y - .045, bottom=.175, wspace=.18)
    axD = [fig.add_subplot(g2[0, i]) for i in (0, 1, 3, 4)]
    panel_perceived(axD, P)
    for (i, j), (_, olab) in zip(((0, 1), (2, 3)), ORDERS):
        p0, p1 = axD[i].get_position(), axD[j].get_position()
        fig.text((p0.x0 + p1.x1) / 2, p0.y1 + .012, olab, ha='center', va='bottom',
                 style='italic', fontsize=FS_LAB)
    p = axD[0].get_position()
    fig.text(.052, (p.y0 + p.y1) / 2, 'Perceived\nexpected value', rotation=90,
             ha='center', va='center', fontsize=FS_LAB, linespacing=1.1)

    sns.despine(fig=fig, offset=3)
    for ax in axes:                      # after the figure-wide call, which re-adds it
        sns.despine(ax=ax, left=True, offset=3)

    # -- headings and keys -----------------------------------------------------
    for ax, letter, title in zip(axes[::2], 'ABC',
                                 ('Prior mean', r'Prior width $\sigma$',
                                  r'Evidence noise $\nu$')):
        dx = -(ax.get_position().x0 - .005) if letter == 'A' else -.022
        heading(fig, ax, letter, title, y=.950, dx=dx)
    key(fig, .275, key_y, PARAM_KEY)
    heading(fig, axD[0], 'D', 'Perceived expected value', y=head_y,
            dx=-(axD[0].get_position().x0 - .005))
    key(fig, .565, head_y + .013, CURVE_KEY)
    return fig


def main(model='5'):
    P = PMCParams(trace_path(model))
    tag = '' if model == '5' else f'_model-{model}'
    par = summarise(P)
    par.to_csv(op.join(OUT, f'fig4_mechanism{tag}_parameter_values.csv'), index=False)
    fig = build(P, par)
    for ext in ('pdf', 'png'):
        fig.savefig(op.join(OUT, f'fig4_mechanism{tag}.{ext}'),
                    dpi=300 if ext == 'png' else None, bbox_inches='tight', pad_inches=.03)
    print(f'saved {OUT}/fig4_mechanism{tag}.pdf  '
          f'(shared prior shift: {P.shared_prior_shift})')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='5',
                    help="model label: '5' (shared prior shift, the paper model) or "
                         "'1' (risky and safe prior means free to move apart)")
    main(ap.parse_args().model)
