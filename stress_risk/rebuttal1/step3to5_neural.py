"""R1.2: risky vs safe options in the decoded parietal signal.

Three questions, all on the SAME matched-numerosity subset so they are comparable:

  3. Is the stress-induced shift in neural coding (E_dif) different for risky and
     safe options once the numerosity ranges are matched?  (already answered on the
     full range: BF10 = 0.18; the open worry was the range mismatch)
  4. At identical numerosity, does decoding ERROR differ by option type, and is the
     shrinkage slope steeper for risky options?  (R1's prediction)
  5. Is the decoded posterior WIDER or NARROWER for risky options?

Decoding is always of the FIRST-presented option (single-trial betas are estimated
at 'stimulus 1'), so "risky option" == risky_first.
"""
import os.path as op
import sys

import numpy as np
import pandas as pd
import pingouin as pg
import statsmodels.formula.api as smf

sys.path.insert(0, op.dirname(op.abspath(__file__)))
from common import load_decoded  # noqa: E402

OUT = '/Users/gdehol/git/stress_risk/notes/rebuttal1/results'


def build():
    within, across = load_decoded()
    w2 = within[within.session == 2].drop(columns='session')
    d = across.merge(w2.rename(columns={'E': 'E_within', 'sd': 'sd_within'}),
                     on=['subject', 'trial_nr'], how='inner', validate='one_to_one')
    d = d.rename(columns={'E': 'E_across', 'sd': 'sd_across'})
    d['E_dif'] = d.E_across - d.E_within
    d['err'] = d.E_within - d.log_n1                 # decoding error, within-session
    d['option'] = np.where(d.risky_first, 'risky', 'safe')
    return d


def overlap(d):
    """Numerosity range presented as BOTH a risky and a safe first option."""
    lo = d.groupby('option').n1.min().max()
    hi = d.groupby('option').n1.max().min()
    return lo, hi


def line(t, p, bf=None, extra=''):
    s = f"t={t:+.3f}  p={p:.3f}"
    if bf is not None:
        s += f"  BF10={bf:.2f}"
    return s + extra


def main():
    d = build()
    lo, hi = overlap(d)
    print(f"trials merged: {len(d)}  subjects: {d.subject.nunique()}")
    for o, g in d.groupby('option'):
        print(f"  {o:5s} n1 range {g.n1.min():.1f} - {g.n1.max():.1f}   n={len(g)}")
    m = d[(d.n1 >= lo) & (d.n1 <= hi)].copy()
    print(f"\nOVERLAPPING RANGE: {lo:.1f} - {hi:.1f} coins  "
          f"({len(m)}/{len(d)} trials = {len(m)/len(d):.0%})")
    for o, g in m.groupby('option'):
        print(f"  {o:5s} n={len(g)}  mean n1={g.n1.mean():.1f}")

    # ---------------- step 3: E_dif, risky vs safe, matched range ----------------
    # Three defensible estimators, and they do NOT agree, so all three are reported.
    # (a) plain subject mean over the common range - still confounded, the risky
    #     trials average n1 = 18.3 against 15.8 for safe;
    # (b) plain subject mean over exactly-matched payoffs;
    # (c) mean per payoff first, then averaged - the properly matched estimator,
    #     but it rests on ~7 risky trials per participant.
    print("\n=== 3. Shift in neural coding (E_dif), risky vs safe ===")
    exact = sorted(set(m.loc[m.option == 'risky', 'n1']) & set(m.loc[m.option == 'safe', 'n1']))
    e = m[m.n1.isin(exact)]
    ests = {
        'plain mean, range 7-28': d.groupby(['subject', 'option']).E_dif.mean().unstack(),
        'plain mean, exact payoff': e.groupby(['subject', 'option']).E_dif.mean().unstack(),
        'per-payoff then averaged': (e.groupby(['subject', 'n1', 'option']).E_dif.mean()
                                     .unstack().dropna().groupby('subject').mean()),
    }
    for tag, s in ests.items():
        s = s.dropna()
        r = pg.ttest(s['risky'], s['safe'], paired=True)
        print(f"  {tag:26s} n={len(s)}  risky {s['risky'].mean():+.4f}  "
              f"safe {s['safe'].mean():+.4f}  "
              f"{line(r['T'].iloc[0], r['p-val'].iloc[0], float(r['BF10'].iloc[0]))}")
    print("  -> the conclusion is estimator-dependent; the matched estimator has only")
    print("     ~7 risky trials per participant.")

    s = ests['per-payoff then averaged'].dropna()
    grp = e.groupby('subject').group.first().reindex(s.index)
    s = s.assign(group=grp, diff=s['risky'] - s['safe'])
    print("\n  Matched estimator, split by group:")
    for gv, name in [(0, 'control'), (1, 'stress')]:
        x = s[s.group == gv]
        r = pg.ttest(x['risky'], x['safe'], paired=True)
        print(f"    {name:8s} n={len(x)}  risky {x['risky'].mean():+.4f}  "
              f"safe {x['safe'].mean():+.4f}  "
              f"{line(r['T'].iloc[0], r['p-val'].iloc[0], float(r['BF10'].iloc[0]))}")
    r = pg.ttest(s.loc[s.group == 1, 'diff'], s.loc[s.group == 0, 'diff'], correction=True)
    print("  The reviewer's prediction is the option x group interaction "
          "(risky shift > safe shift under stress):")
    print(f"    stress risky-safe {s.loc[s.group == 1, 'diff'].mean():+.4f}  "
          f"control {s.loc[s.group == 0, 'diff'].mean():+.4f}  "
          f"{line(r['T'].iloc[0], r['p-val'].iloc[0], float(r['BF10'].iloc[0]))}")
    print("    Note the sign: within the stress group the shift is larger for the SAFE")
    print("    option, i.e. opposite to the predicted direction, but the interaction")
    print("    itself is not credible.")

    g = m.groupby(['subject', 'option']).agg(E_dif=('E_dif', 'mean'),
                                             group=('group', 'first')).reset_index()
    print("  group effect (stress vs control) within the overlap:")
    for o in ['risky', 'safe']:
        x = g[g.option == o]
        r = pg.ttest(x.loc[x.group == 1, 'E_dif'], x.loc[x.group == 0, 'E_dif'],
                     correction=True)
        print(f"    {o:5s} {line(r['T'].iloc[0], r['p-val'].iloc[0], float(r['BF10'].iloc[0]))}")

    # ---------------- step 4: decoding error --------------------------------
    # The safe option takes only 5 numerosities (7,10,14,20,28) while the risky one
    # is near-continuous, so a common RANGE is not a matched DISTRIBUTION: inside
    # 7-28 the risky mean is still 18.3 vs 15.8 for safe. Decoding error depends
    # steeply on numerosity, so the comparison must be made at IDENTICAL n1.
    print("\n=== 4. Decoding error at matched numerosity ===")
    exact = sorted(set(m.loc[m.option == 'risky', 'n1']) & set(m.loc[m.option == 'safe', 'n1']))
    e = m[m.n1.isin(exact)]
    print(f"  exact-match numerosities: {[int(x) for x in exact]}")
    naive = m.groupby(['subject', 'option']).err.mean().unstack().dropna()
    rn = pg.ttest(naive['risky'], naive['safe'], paired=True)
    print(f"  [range-matched only, CONFOUNDED by numerosity - not for reporting] "
          f"{line(rn['T'].iloc[0], rn['p-val'].iloc[0], float(rn['BF10'].iloc[0]))}")
    # per (subject, numerosity) then averaged, so every comparison is within-n1
    cell = e.groupby(['subject', 'n1', 'option']).err.mean().unstack()
    cell = cell.dropna()
    s = cell.groupby('subject').mean()
    r = pg.ttest(s['risky'], s['safe'], paired=True)
    print(f"  Test 1 (the gate, exact n1 match): n={len(s)}  "
          f"risky {s['risky'].mean():+.4f}  safe {s['safe'].mean():+.4f}  "
          f"{line(r['T'].iloc[0], r['p-val'].iloc[0], float(r['BF10'].iloc[0]))}")
    mm = m.copy()
    mm['ln'] = mm.log_n1 - mm.log_n1.mean()
    mm['risky'] = (mm.option == 'risky').astype(float)
    fit = smf.mixedlm('err ~ ln * risky', mm, groups=mm.subject,
                      re_formula='~ln').fit(method='lbfgs')
    print("  Test 2 (shrinkage slope):")
    for term in ['ln', 'risky', 'ln:risky']:
        print(f"    {term:10s} beta={fit.params[term]:+.4f}  "
              f"z={fit.tvalues[term]:+.3f}  p={fit.pvalues[term]:.4f}")
    print(f"    -> slope of decoded on presented: risky {1+fit.params['ln']+fit.params['ln:risky']:.3f}, "
          f"safe {1+fit.params['ln']:.3f}   (1.0 = no shrinkage)")

    # ---------------- step 5: posterior width --------------------------------
    print("\n=== 5. Width of the decoded posterior p(n|a) at matched numerosity ===")
    cell = e.groupby(['subject', 'n1', 'option']).sd_within.mean().unstack().dropna()
    s = cell.groupby('subject').mean()
    r = pg.ttest(s['risky'], s['safe'], paired=True)
    print(f"  exact n1 match: n={len(s)}  risky {s['risky'].mean():.4f}  safe {s['safe'].mean():.4f}  "
          f"{line(r['T'].iloc[0], r['p-val'].iloc[0], float(r['BF10'].iloc[0]))}")

    # ---------------- how much can these tests say? --------------------------
    rr = pd.read_csv('/Users/gdehol/data/ds-stressrisk/interim_sum_data/'
                     'within-ses-decod_r-sds.csv')
    rr = rr[rr.session == 2]
    print(f"\n  Decoder quality (session 2): mean r = {rr.r.mean():.3f}, "
          f"median {rr.r.median():.3f}, {(rr.r > 0).sum()}/{len(rr)} subjects positive.")
    print("  With decodability this low the shrinkage and width tests have little "
          "signal;\n  report the Bayes factors and treat a null as uninformative.")

    m.to_csv(op.join(OUT, 'rebuttal_neural_matched_trials.csv'), index=False)
    print(f"\nsaved {OUT}/rebuttal_neural_matched_trials.csv")


if __name__ == '__main__':
    main()
