"""R1.3: contrast the two groups at session 1 on all six PMC parameters.

Context that matters for the interpretation: participants were assigned to groups
after balancing on session-1 RNP, choice consistency and decoding accuracy
(stress_risk/subject_selection/). A null on those measures at baseline is
therefore partly by design and is not independent evidence. The PMC parameters
were NOT balanced on, so this is the informative check.

Two estimates of each contrast, because they can disagree:
  (a) population level - the group + session:group coefficients of the _mu terms;
  (b) subject level    - each participant's own posterior parameter value at
      session 1, then the difference of group means. This carries the hierarchical
      shrinkage and the per-subject uncertainty.

Structural caveat: risky_prior_mu and safe_prior_mu carry an INTERCEPT ONLY. A
baseline group difference in either can be expressed only through the shared
prior_mu regressor, so their contrasts are identical by construction - one test,
not two.
"""
import os.path as op
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, op.dirname(op.abspath(__file__)))
from common import PMCParams, design, softplus  # noqa: E402

OUT = '/Users/gdehol/git/stress_risk/notes/rebuttal1/results'
PARAMS = ['risky_prior_mu', 'safe_prior_mu', 'risky_prior_std', 'safe_prior_std',
          'n1_evidence_sd', 'n2_evidence_sd']
IS_SD = lambda p: ('sd' in p) or ('std' in p)


def population_cell(P, par, session, group):
    """Posterior draws of `par` in one cell, on its interpretable scale."""
    if 'prior_mu' in par:                       # intercept + the shared shift
        v = P.draws(par)[:, 0] + P.value('prior_mu', session, group)
    else:
        v = P.value(par, session, group)
    return softplus(v) if IS_SD(par) else v


def subject_values(P, par, session, groups):
    """(draw, subject) values of `par` at `session`, each at that subject's group."""
    out = []
    for i, s in enumerate(P.subjects):
        g = groups[i]
        if 'prior_mu' in par:
            X = design(session, g, False)
            v = P.draws(par, s)[:, 0] + P.draws('prior_mu', s) @ X
        else:
            v = P.draws(par, s) @ design(session, g, True)
        out.append(softplus(v) if IS_SD(par) else v)
    return np.stack(out, 1)


def fmt(d):
    return (f"{d.mean():+.4f} [{np.percentile(d, 2.5):+.4f}, "
            f"{np.percentile(d, 97.5):+.4f}]")


def main():
    P = PMCParams()
    grp = (pd.read_csv('/Users/gdehol/data/ds-stressrisk/group_assignmentList.csv',
                       index_col=1)['group'].reindex(P.subjects).values)
    stress = grp == 1
    control = grp == 0
    print(f"subjects in the trace: {len(grp)}  (stress {stress.sum()}, "
          f"control {control.sum()})\n")

    rows = []
    print("=== Session-1 group contrast (stress - control) ===")
    print(f"{'parameter':17s} {'population level':38s} {'P(>0)':>6s}  "
          f"{'subject level':38s} {'P(>0)':>6s}")
    for par in PARAMS:
        pop = population_cell(P, par, 1, 1) - population_cell(P, par, 1, 0)
        sub_all = subject_values(P, par, 1, grp)
        sub = sub_all[:, stress].mean(1) - sub_all[:, control].mean(1)
        print(f"{par:17s} {fmt(pop):38s} {np.mean(pop > 0):6.3f}  "
              f"{fmt(sub):38s} {np.mean(sub > 0):6.3f}")
        rows.append(dict(parameter=par, level='population', mean=pop.mean(),
                         lo=np.percentile(pop, 2.5), hi=np.percentile(pop, 97.5),
                         p_pos=np.mean(pop > 0)))
        rows.append(dict(parameter=par, level='subject', mean=sub.mean(),
                         lo=np.percentile(sub, 2.5), hi=np.percentile(sub, 97.5),
                         p_pos=np.mean(sub > 0)))

    print("\n=== Size of each baseline contrast against its own yardsticks ===")
    print(f"{'parameter':17s} {'baseline':>10s} {'ses-2 gap':>10s} "
          f"{'interaction':>12s} {'baseline/inter':>15s} {'between-subj SD':>16s}")
    for par in PARAMS:
        b = population_cell(P, par, 1, 1) - population_cell(P, par, 1, 0)
        s2 = population_cell(P, par, 2, 1) - population_cell(P, par, 2, 0)
        inter = ((population_cell(P, par, 2, 1) - population_cell(P, par, 1, 1))
                 - (population_cell(P, par, 2, 0) - population_cell(P, par, 1, 0)))
        sd_between = subject_values(P, par, 1, grp).mean(0).std(ddof=1)
        ratio = abs(b.mean()) / abs(inter.mean()) if abs(inter.mean()) > 1e-9 else np.nan
        print(f"{par:17s} {b.mean():+10.4f} {s2.mean():+10.4f} {inter.mean():+12.4f} "
              f"{ratio:15.2f} {sd_between:16.4f}")

    print("\n=== Equivalence: is each baseline gap small on the between-subject scale? ===")
    print("ROPE = +/- 0.1 between-subject SD of that parameter at session 1.")
    joint = None
    for par in PARAMS:
        b = population_cell(P, par, 1, 1) - population_cell(P, par, 1, 0)
        rope = 0.1 * subject_values(P, par, 1, grp).mean(0).std(ddof=1)
        inside = np.abs(b) < rope
        joint = inside if joint is None else (joint & inside)
        print(f"  {par:17s} ROPE=+/-{rope:.4f}   P(inside)={inside.mean():.3f}")
    print(f"\n  P(all six inside their ROPE simultaneously) = {joint.mean():.3f}")
    print("  (risky_prior_mu and safe_prior_mu are the same contrast by construction,")
    print("   so this is five independent quantities, not six.)")

    pd.DataFrame(rows).to_csv(op.join(OUT, 'rebuttal_baseline_contrasts.csv'), index=False)
    print(f"\nsaved {OUT}/rebuttal_baseline_contrasts.csv")


if __name__ == '__main__':
    main()


def bound_and_coupling():
    """Two things the raw baseline table does not settle.

    (1) How much of the reported interaction could a baseline gap manufacture?
        Under regression to the mean with test-retest correlation rho, a baseline
        gap D0 produces an expected difference in change of -D0*(1-rho). The worst
        case is rho = 0, so |spurious interaction| <= |D0|. That gives a hard upper
        bound without having to estimate rho.

    (2) Could the one near-credible baseline imbalance (evidence noise on the first
        option) be driving the prior shift? If baseline noise and the subject's
        prior shift are unrelated, the imbalance cannot be the mechanism.
    """
    import numpy as np
    import pandas as pd
    P = PMCParams()
    grp = (pd.read_csv('/Users/gdehol/data/ds-stressrisk/group_assignmentList.csv',
                       index_col=1)['group'].reindex(P.subjects).values)

    print("\n=== Worst-case regression-to-the-mean bound ===")
    print("  |spurious interaction| <= |baseline gap|   (attained only if rho = 0)")
    print(f"  {'parameter':17s} {'|baseline|':>11s} {'|interaction|':>14s} "
          f"{'max share explained':>21s}")
    for par in PARAMS:
        b = population_cell(P, par, 1, 1) - population_cell(P, par, 1, 0)
        inter = ((population_cell(P, par, 2, 1) - population_cell(P, par, 1, 1))
                 - (population_cell(P, par, 2, 0) - population_cell(P, par, 1, 0)))
        share = abs(b.mean()) / abs(inter.mean())
        print(f"  {par:17s} {abs(b.mean()):11.4f} {abs(inter.mean()):14.4f} "
              f"{min(share, 1.0):20.1%}{'' if share <= 1 else '  (gap exceeds effect)'}")

    print("\n=== Direction of the risk ===")
    b = population_cell(P, 'risky_prior_mu', 1, 1) - population_cell(P, 'risky_prior_mu', 1, 0)
    print(f"  baseline gap in the prior mean = {b.mean():+.4f} (stress lower), so "
          f"regression to the\n  mean would push the stress group UP - the same direction "
          f"as the reported effect.\n  The bound is therefore the relevant guarantee, not "
          f"the sign.")

    print("\n=== Is the baseline noise imbalance coupled to the prior shift? ===")
    from step7_physiology_bayes import partial_corr_rows
    base_nu1 = subject_values(P, 'n1_evidence_sd', 1, grp)          # (draw, subject)
    shift = np.stack([P.draws('prior_mu', s) @ (design(2, g, False) - design(1, g, False))
                      for s, g in zip(P.subjects, grp)], 1)          # (draw, subject)
    r = np.array([np.corrcoef(base_nu1[i], shift[i])[0, 1] for i in range(len(shift))])
    rp = partial_corr_rows(base_nu1, shift.mean(0), grp.astype(float))
    print(f"  baseline n1_evidence_sd vs prior shift, per draw:  "
          f"r = {r.mean():+.3f} [{np.percentile(r,2.5):+.3f}, {np.percentile(r,97.5):+.3f}]")
    print(f"  same, group partialled out:                        "
          f"r = {rp.mean():+.3f} [{np.percentile(rp,2.5):+.3f}, {np.percentile(rp,97.5):+.3f}]"
          f"   P(r>0) = {np.mean(rp>0):.3f}")


if __name__ == '__main__':
    bound_and_coupling()
