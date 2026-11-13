"""Model-free baseline check: did the groups already differ in risky choice at session 1?

Complements step6 (which contrasts the PMC parameters). Here the outcome is raw
P(chose risky) per subject at session 1, before any stress induction.

  (a) per-subject proportion, stress vs control: Welch / Student t, Mann-Whitney,
      permutation test, JZS Bayes factor;
  (b) trial-level logistic regression with subject-clustered SEs, with and without
      the payoff ratio as a covariate, to ask whether the gap is a shift
      (intercept) or a flatter psychometric curve (slope).

Runs in an env with pingouin + statsmodels and the package importable, e.g.
  PYTHONPATH=<repo> ~/mambaforge/envs/tms_risk/bin/python step11_baseline_choice.py
"""
import os.path as op
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg
import seaborn as sns
import statsmodels.formula.api as smf

sys.path.insert(0, op.dirname(op.abspath(__file__)))
from common import get_behavior  # noqa: E402
from make_figures import C_RISKY, C_SAFE, C_REF, save  # noqa: E402  (also sets rcParams)

C_CTRL, C_STRESS = C_SAFE, C_RISKY


def main():
    b = get_behavior().dropna(subset=['chose_risky']).copy()
    b['chose_risky'] = b.chose_risky.astype(float)
    b['lr'] = np.log(b.n_risky / b.n_safe)

    s = (b.groupby(['subject', 'group', 'session']).chose_risky.mean()
         .unstack('session').reset_index())
    st, ct = s.loc[s.group == 1, 1].values, s.loc[s.group == 0, 1].values

    print("=== Session-1 P(chose risky), per subject ===")
    print(f"  control {ct.mean():.3f} (SD {ct.std(ddof=1):.3f}, n={len(ct)})   "
          f"stress {st.mean():.3f} (SD {st.std(ddof=1):.3f}, n={len(st)})")
    tt = pg.ttest(st, ct, correction=False).iloc[0]
    tw = pg.ttest(st, ct, correction=True).iloc[0]
    mw = pg.mwu(st, ct).iloc[0]
    rng = np.random.default_rng(0)
    pooled, n1, d0 = np.r_[st, ct], len(st), st.mean() - ct.mean()
    null = np.array([(lambda p: p[:n1].mean() - p[n1:].mean())(rng.permutation(pooled))
                     for _ in range(20000)])
    p_perm = np.mean(np.abs(null) >= abs(d0))
    print(f"  diff = {d0:+.3f}, 95% CI [{tt['CI95%'][0]:+.3f}, {tt['CI95%'][1]:+.3f}]")
    print(f"  Student t({tt['dof']:.0f}) = {tt['T']:.2f}, p = {tt['p-val']:.4f}, "
          f"d = {tt['cohen-d']:.2f}, BF10 = {tt['BF10']}")
    print(f"  Welch   t({tw['dof']:.1f}) = {tw['T']:.2f}, p = {tw['p-val']:.4f}")
    print(f"  Mann-Whitney U = {mw['U-val']:.1f}, p = {mw['p-val']:.4f}")
    print(f"  permutation (20k) p = {p_perm:.4f}")
    t2 = pg.ttest(s.loc[s.group == 1, 2], s.loc[s.group == 0, 2]).iloc[0]
    print(f"  (session 2: t = {t2['T']:.2f}, p = {t2['p-val']:.3f}, BF10 = {t2['BF10']})")

    print("\n=== Session-1 trial-level logit, SEs clustered by subject ===")
    s1 = b[b.session == 1]
    for f in ['chose_risky ~ group', 'chose_risky ~ group + lr',
              'chose_risky ~ group * lr + risky_first']:
        m = smf.logit(f, s1).fit(disp=0, cov_type='cluster',
                                 cov_kwds={'groups': s1.subject})
        terms = [t for t in m.params.index if 'group' in t]
        print(f"  {f:40s} " + "  ".join(
            f"{t} = {m.params[t]:+.3f} (z = {m.tvalues[t]:+.2f}, p = {m.pvalues[t]:.3f})"
            for t in terms))

    # ---------------------------------------------------------------- figure
    fig, axes = plt.subplots(1, 2, figsize=(5.2, 2.3), gridspec_kw=dict(wspace=.45))
    ax = axes[0]
    for x, v, c in [(0, ct, C_CTRL), (1, st, C_STRESS)]:
        ax.scatter(x + rng.uniform(-.12, .12, len(v)), v, s=9, color=c, alpha=.45, lw=0)
        ci = 1.96 * v.std(ddof=1) / np.sqrt(len(v))
        ax.errorbar(x + .28, v.mean(), ci, fmt='o', color=c, ms=4, capsize=0, lw=1.4)
    ax.axhline(.5, color=C_REF, ls='--', lw=.8, zorder=0)
    ax.set_xticks([0, 1], ['Control', 'Stress'])
    ax.set_xlim(-.4, 1.6)
    ax.set_ylabel('P(chose risky), session 1')
    ax.text(.5, 1.02, f"Δ = {d0:+.3f}, t({tt['dof']:.0f}) = {tt['T']:.2f}, "
            f"p = {tt['p-val']:.3f}\nBF$_{{10}}$ = {tt['BF10']}",
            transform=ax.transAxes, ha='center', va='bottom', fontsize=6.5)

    ax = axes[1]
    for g, c, lab in [(0, C_CTRL, 'Control'), (1, C_STRESS, 'Stress')]:
        d = s1[s1.group == g]
        per = d.groupby(['subject', 'bin(risky/safe)'], observed=True)[
            ['chose_risky', 'lr']].mean().reset_index()
        m = per.groupby('bin(risky/safe)', observed=True).agg(
            x=('lr', 'mean'), y=('chose_risky', 'mean'), e=('chose_risky', 'sem'))
        ax.errorbar(m.x, m.y, m.e, fmt='o-', color=c, ms=3, lw=1.2, capsize=0, label=lab)
    ax.axhline(.5, color=C_REF, ls='--', lw=.8, zorder=0)
    ax.set_xlabel('log(risky / safe payoff)')
    ax.set_ylabel('P(chose risky), session 1')
    ax.legend(loc='upper left')
    save(fig, 'fig_baseline_choice')

    group_session_figure(b, s)


def probit_parameters(b):
    """RNP and slope per group x session, from the paper's probit model.

    Trace: bambi-RNP-fit_trace_model-paper (the paper model refit in current bambi;
    reproduces the published RNP interaction 0.066, p_bayes = 0.031). Linear
    predictor a + b*x, x = log(risky/safe), session numeric 1/2, group 0/1;
    RNP = exp(a / b), the safe/risky payoff ratio at indifference (0.55 = neutral).

    Group contrasts are read off the population-level (fixed-effect) posterior.
    Do NOT t-test the per-subject estimates of this model: `group` is a fixed effect,
    so each subject is shrunk toward its OWN group's mean, which shrinks within-group
    spread and makes a frequentist test of the group difference anti-conservative.
    The frequentist check uses independent per-subject probit fits (no pooling)
    instead. The per-subject posterior medians are returned for display only.
    """
    import arviz as az
    import statsmodels.api as sm
    from common import COGMODELS
    P = az.from_netcdf(op.join(COGMODELS, 'bambi-RNP-fit_trace_model-paper.netcdf')).posterior
    f = lambda k: P[k].values.reshape(-1, *P[k].shape[2:])

    def cell(ses, g, subject_level=False):
        a = f('Intercept') + ses * f('session') + g * f('group') + ses * g * f('session:group')
        s = f('x') + ses * f('x:session') + g * f('x:group') + ses * g * f('x:session:group')
        if subject_level:
            a = a[:, None] + f('1|subject') + ses * f('session|subject')
            s = s[:, None] + f('x|subject') + ses * f('x:session|subject')
        return {'rnp': np.exp(a / s), 'slope': s, 'a': a}

    subjects = P.subject__factor_dim.values.astype(int)
    grp = b.groupby('subject').group.first().reindex(subjects).values
    display, pop, stats = {}, {}, {}
    for par in ['rnp', 'slope']:
        d = pd.DataFrame({'subject': subjects, 'group': grp})
        for ses in [1, 2]:
            r = np.stack([cell(ses, g, True)[par][:, i] for i, g in enumerate(grp)], 1)
            d[f's{ses}'] = np.median(r, 0)
        display[par] = d
        c = {(ses, g): cell(ses, g)[par] for ses in [1, 2] for g in [0, 1]}
        pop[par] = c
        stats[par] = {'ses1': c[1, 1] - c[1, 0], 'ses2': c[2, 1] - c[2, 0],
                      'did': (c[2, 1] - c[1, 1]) - (c[2, 0] - c[1, 0])}

    # independent (unpooled) per-subject probit fits, session 1
    rows = []
    for (sub, g), d in b[b.session == 1].groupby(['subject', 'group']):
        m = sm.GLM(d.chose_risky, sm.add_constant(d.lr),
                   family=sm.families.Binomial(sm.families.links.Probit())).fit()
        a, s = m.params['const'], m.params['lr']
        rows.append(dict(subject=sub, group=g, rnp=np.exp(a / s), slope=s))
    ind = pd.DataFrame(rows)
    for par in ['rnp', 'slope']:
        x1, x0 = ind[par][ind.group == 1], ind[par][ind.group == 0]
        stats[par]['ind_t'] = pg.ttest(x1, x0).iloc[0]
        stats[par]['ind_u'] = pg.mwu(x1, x0).iloc[0]
        stats[par]['ind_med'] = (x0.median(), x1.median())

    # model-predicted choice curves: P(risky | x) averaged over the subjects of a
    # group, per posterior draw (same aggregation as the plotted data)
    from scipy.stats import norm
    xb = b.groupby('bin(risky/safe)', observed=True).lr.mean()
    xg = np.linspace(xb.min() - .03, xb.max() + .03, 60)
    thin = slice(None, None, 8)
    curves = {}
    for ses in [1, 2]:
        for g in [0, 1]:
            idx = np.where(grp == g)[0]
            c = cell(ses, g, True)
            a, sl = c['a'][thin][:, idx], c['slope'][thin][:, idx]
            curves[ses, g] = norm.cdf(a[..., None] + sl[..., None] * xg).mean(1)
    stats['curves'] = (xg, curves)
    return display, pop, stats


def group_session_figure(b, s):
    """One-figure summary for the group: raw choice, RNP and slope, by group x
    session, plus the choice curves. Each panel's statistics sit under it."""
    s = s.rename(columns={1: 's1', 2: 's2'})
    s['d'] = s.s2 - s.s1
    rho = np.corrcoef(s.s1, s.s2)[0, 1]
    d0 = s.s1[s.group == 1].mean() - s.s1[s.group == 0].mean()
    display, pop, st = probit_parameters(b)

    ci = lambda d: f"{d.mean():+.2f} [{np.percentile(d, 2.5):+.2f}, {np.percentile(d, 97.5):+.2f}]"
    pb = lambda d: min(np.mean(d > 0), np.mean(d < 0))

    # ---- statistics text, one block per panel
    def tline(x1, x0, lab):
        t = pg.ttest(x1, x0).iloc[0]
        return (f"{lab}:  Δ = {x1.mean() - x0.mean():+.3f},  t({t['dof']:.0f}) = "
                f"{t['T']:.2f},  p = {t['p-val']:.3f},  BF10 = {t['BF10']}")
    g1, g0 = s.group == 1, s.group == 0
    txt_raw = [tline(s.s1[g1], s.s1[g0], 'Session 1'),
               tline(s.s2[g1], s.s2[g0], 'Session 2'),
               tline(s.d[g1], s.d[g0], 'Group × session'),
               f"Regression to the mean predicts {-d0 * (1 - rho):+.3f}  (r = {rho:.2f})"]

    def mline(par):
        z = st[par]
        t, u = z['ind_t'], z['ind_u']
        return [f"Session 1:  {ci(z['ses1'])},  p(bayes) = {pb(z['ses1']):.2f}",
                f"Session 2:  {ci(z['ses2'])},  p(bayes) = {pb(z['ses2']):.2f}",
                f"Group × session:  {ci(z['did'])},  p(bayes) = {pb(z['did']):.3f}",
                f"Unpooled fits, session 1:  t({t['dof']:.0f}) = {t['T']:.2f}, "
                f"p = {t['p-val']:.2f};  U test p = {u['p-val']:.2f}"]

    print("\n=== Probit parameters, stress - control ===")
    for par in ['rnp', 'slope']:
        print(par, *mline(par), sep='\n  ')

    # ---- layout: one row, two short stat lines per panel, nothing else
    fig, axes = plt.subplots(1, 5, figsize=(9.6, 2.7), gridspec_kw=dict(
        width_ratios=[1, 1, 1, 1, 1], wspace=.6, left=.065, right=.99, top=.70,
        bottom=.17))

    paired_panel(axes[0], s[['subject', 'group', 's1', 's2']], 'P(chose risky)', .5)
    paired_panel(axes[1], display['rnp'], 'RNP (0.55 = risk neutral)', .55,
                 means=pop['rnp'])
    paired_panel(axes[2], display['slope'], 'Slope', None, means=pop['slope'])
    axes[1].set_ylim(0, 1.3)
    choice_curves(axes[3], b, st['curves'], 1)
    choice_curves(axes[4], b, st['curves'], 2)
    axes[3].set_ylabel('P(chose risky)')
    axes[4].set_yticklabels([])
    # d and e are one comparison: pull them together and widen them
    p3, p4 = axes[3].get_position(), axes[4].get_position()
    w = (p4.x1 - p3.x0 - .025) / 2
    axes[3].set_position([p3.x0, p3.y0, w, p3.height])
    axes[4].set_position([p3.x0 + w + .025, p4.y0, w, p4.height])
    for ax in axes[3:]:
        ax.set_xlabel('log(risky / safe)')

    p = lambda x: f"{x:.2f}" if x >= .01 else f"{x:.3f}"
    t_base = pg.ttest(s.s1[g1], s.s1[g0]).iloc[0]['p-val']
    t_did = pg.ttest(s.d[g1], s.d[g0]).iloc[0]['p-val']
    stats_txt = [
        [f"Baseline: p = {p(t_base)}", f"Group × session: p = {p(t_did)}"],
        [f"Baseline: p = {p(st['rnp']['ind_t']['p-val'])}",
         f"Group × session: p = {p(pb(st['rnp']['did']))}"],
        [f"Baseline: p = {p(st['slope']['ind_t']['p-val'])}",
         f"Group × session: p = {p(pb(st['slope']['did']))}"],
        ['Fitted choice curves'], ['Fitted choice curves']]
    titles = ['Proportion of risky choices', 'Risk attitude', 'Choice consistency',
              'Session 1 (baseline)', 'Session 2']
    for ax, lab, ttl, lines in zip(axes, 'abcde', titles, stats_txt):
        ax.text(-.32, 1.30, lab, transform=ax.transAxes, fontsize=8, ha='left',
                va='bottom', weight='bold', family='Arial')
        ax.text(-.32 + (.13 if lab in 'abc' else .1), 1.30, ttl, transform=ax.transAxes,
                fontsize=8, ha='left', va='bottom')
        if lines:
            ax.text(-.32 + (.13 if lab in 'abc' else .1), 1.26, '\n'.join(lines),
                    transform=ax.transAxes, fontsize=6.5, ha='left', va='top',
                    color='0.4', linespacing=1.4)

    fig.text(.015, .975, 'At baseline the stress group made slightly fewer risky choices, '
             'but its risk attitude and choice consistency did not differ',
             fontsize=8.5, ha='left', va='top')
    save(fig, 'fig_group_session_choice')


def paired_panel(ax, d, ylabel, ref, means=None, seed=1):
    """Per-subject values in session 1 and 2, joined. The summary marker is the
    across-subject mean with 95% CI, or, if `means` maps (session, group) to
    posterior draws, the model's population-level estimate with 95% CrI."""
    rng = np.random.default_rng(seed)
    for g, c, x0 in [(0, C_CTRL, 0), (1, C_STRESS, 2.4)]:
        dg = d[d.group == g]
        jit = rng.uniform(-.07, .07, len(dg))
        xs = np.c_[x0 + jit, x0 + 1 + jit]
        for (a, b_), (y1, y2) in zip(xs, dg[['s1', 's2']].values):
            ax.plot([a, b_], [y1, y2], color='0.82', lw=.4, zorder=1)
        ax.scatter(xs.ravel(), dg[['s1', 's2']].values.ravel(), s=6, color=c, alpha=.35,
                   lw=0, zorder=2)
        if means is None:
            m = dg[['s1', 's2']].mean().values
            lo = m - 1.96 * dg[['s1', 's2']].sem().values
            hi = m + 1.96 * dg[['s1', 's2']].sem().values
        else:
            dr = [means[ses, g] for ses in (1, 2)]
            m = np.array([v.mean() for v in dr])
            lo = np.array([np.percentile(v, 2.5) for v in dr])
            hi = np.array([np.percentile(v, 97.5) for v in dr])
        xm = [x0 - .32, x0 + 1.32]
        ax.plot(xm, m, '-', color=c, lw=1.3, zorder=3)
        ax.vlines(xm, lo, hi, color=c, lw=1.3, zorder=3)
        ax.plot(xm, m, 'o', color=c, ms=4.5, mec='white', mew=.6, zorder=4)
    if ref is not None:
        ax.axhline(ref, color='0.7', ls='--', lw=.6, zorder=0)
    ax.set_xticks([0, 1, 2.4, 3.4], ['S1', 'S2', 'S1', 'S2'])
    ax.set_xlim(-.6, 4.0)
    for x, lab, c in [(.5, 'Control', C_CTRL), (2.9, 'Stress', C_STRESS)]:
        ax.text(x, -.2, lab, color=c, transform=ax.get_xaxis_transform(),
                ha='center', va='top', fontsize=7.5)
    ax.set_ylabel(ylabel)
    sns.despine(ax=ax, offset=4, trim=True)


def choice_curves(ax, b, curves, ses):
    """One session: model-predicted curve per group (line, 95% CrI band) and the
    observed subject-averaged proportions per payoff bin (markers)."""
    xg, cv = curves
    for g, c in [(0, C_CTRL), (1, C_STRESS)]:
        y = cv[ses, g]
        ax.fill_between(xg, np.percentile(y, 2.5, 0), np.percentile(y, 97.5, 0),
                        color=c, alpha=.18, lw=0, zorder=1)
        ax.plot(xg, y.mean(0), color=c, lw=1.2, zorder=2)
        d = b[(b.group == g) & (b.session == ses)]
        per = d.groupby(['subject', 'bin(risky/safe)'], observed=True)[
            ['chose_risky', 'lr']].mean().reset_index()
        m = per.groupby('bin(risky/safe)', observed=True)[['lr', 'chose_risky']].mean()
        ax.plot(m.lr, m.chose_risky, 'o', color=c, ms=3.2, mec='white', mew=.5, zorder=3)
    ax.axhline(.5, color='0.7', ls='--', lw=.6, zorder=0)
    ax.set_xlim(xg[0] - .02, xg[-1] + .02)
    ax.set_xticks([.4, .7, 1.0])
    ax.set_ylim(.1, .9)
    ax.set_yticks([.1, .3, .5, .7, .9])
    tf = ax.transAxes
    for i, (lab, c) in enumerate([('Control', C_CTRL), ('Stress', C_STRESS)]):
        y = .22 - i * .1
        ax.plot([.56, .68], [y, y], transform=tf, color=c, lw=1.2)
        ax.plot(.62, y, 'o', transform=tf, color=c, ms=3.2, mec='white', mew=.5)
        ax.text(.72, y, lab, transform=tf, color=c, fontsize=6.5, va='center')
    sns.despine(ax=ax, offset=4)

if __name__ == '__main__':
    main()
