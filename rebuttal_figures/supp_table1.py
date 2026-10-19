"""Supplementary Table 1, regenerated with the session coding the model was fitted with.

The published table gave, per group x session cell, the posterior mean and 95% CI of
the six PMC parameters of model 5 (`derivatives/cogmodels/model-5_trace.netcdf`).
It was made in `stress_risk/plots_for_paper/paperFinal_supplements.ipynb` (cell 3),
which evaluated the regression as

    Intercept + session*[s == 2] + group*g + session:group*[s == 2]*g

i.e. with session coded 0/1. The model was fitted with session coded 1/2 (the
design matrices stored in the trace, `constant_data/_dm_*`, have session in {1, 2}
and session:group = session*group), so every published cell sits one session step
too early: "session 1" is an extrapolation to a session 0 and "session 2" holds the
session-1 estimate. Regression coefficients, and therefore every effect in the main
text, are unaffected.

Everything below is computed from the posterior draws; reference values are read
from their sources, never typed:
  * old table      - the stored output of the notebook cell that made it (identical
                     to the published table), and recomputed here with 0/1 coding;
  * main-text      - parsed from the submitted manuscript PDF (needs `pdftotext`;
                     the PDF is kept out of this public repo, so this check is
                     skipped when it is absent);
  * baseline gap   - notes/rebuttal1/results/rebuttal_baseline_contrasts.csv.

Same units as the published table: prior means are in log(CHF) space, the four
SD parameters are softplus-transformed (as bauer does) and are SDs in log space.
CIs are 2.5/97.5 percentiles over all 4 x 1000 draws, as in the original.

Usage:  python supp_table1.py [--bids_folder /Users/gdehol/data/ds-stressrisk]
Writes, next to this script:
  supp_table1.md / .csv              the corrected table (md to paste into Google Docs)
  supp_table1_diff.md / .csv         old vs new, per cell
  supp_table1_checks.md              design-matrix coding, session-1 group differences,
                                     main-text effects, Table S2
Runs in any env with arviz (e.g. ~/mambaforge/envs/tms_risk).
"""
import argparse
import json
import os.path as op
import re
import subprocess

import arviz as az
import numpy as np
import pandas as pd

HERE = op.dirname(op.abspath(__file__))
REPO = op.dirname(HERE)
NOTEBOOK = op.join(REPO, 'stress_risk', 'plots_for_paper', 'paperFinal_supplements.ipynb')
PAPER_PDF = op.join(REPO, 'notes', 'rebuttal1', 'private', 'paper_v1.pdf')   # not in git
BASELINE_CSV = op.join(REPO, 'notes', 'rebuttal1', 'results', 'rebuttal_baseline_contrasts.csv')

# (variable in the trace, label in the published table), in the published order
PARAMS = [('risky_prior_mu', 'risky_prior_mu'), ('safe_prior_mu', 'safe_prior_mu'),
          ('n1_evidence_sd', 'n1_evidence_sd'), ('n2_evidence_sd', 'n2_evidence_sd'),
          ('risky_prior_std', 'risky_prior_sd'), ('safe_prior_std', 'safe_prior_sd')]
CELLS = [(0, 1), (0, 2), (1, 1), (1, 2)]   # (group, session); group 1 = stress
CAPTION = ('Supplementary Table 1: Parameter estimates (mean and confidence interval (CI)) '
           'for all group/session-pairs. Note that the means (mu) and the standard '
           'deviations (sd) are in log-space.')

softplus = lambda x: np.log1p(np.exp(-np.abs(x))) + np.maximum(x, 0)   # bauer's softplus_np
cell_label = lambda g, s: f'Group {g}, Session {s}'


# --------------------------------------------------------------------------- model

def regressors(post, var):
    return [str(r) for r in post[f'{var}_mu'].coords[f'{var}_regressors'].values]


def coefs(post, var):
    """Group-level draws, (n_draws, n_regressors), all chains stacked."""
    return post[f'{var}_mu'].stack(s=('chain', 'draw')).transpose('s', ...).values


def design_row(names, group, session):
    col = {'Intercept': 1., 'session': session, 'group': group, 'session:group': session * group}
    return np.array([col[n] for n in names])


def linear_predictor(post, var, group, session):
    """Untransformed parameter in one cell; model 5 adds the shared prior_mu shift."""
    terms = [var] + (['prior_mu'] if var.endswith('prior_mu') and 'prior_mu_mu' in post else [])
    return sum(coefs(post, t) @ design_row(regressors(post, t), group, session) for t in terms)


def cell_draws(post, var, group, session):
    x = linear_predictor(post, var, group, session)
    return softplus(x) if var.endswith(('_sd', '_std')) else x


def summarise(x):
    lo, hi = np.percentile(x, [2.5, 97.5])
    return dict(mean=np.mean(x), lo=lo, hi=hi, p_pos=np.mean(x > 0))


def make_table(post, session_codes):
    """session_codes maps session 1/2 to the value plugged into the design matrix."""
    rows = []
    for var, label in PARAMS:
        for g, s in CELLS:
            d = summarise(cell_draws(post, var, g, session_codes[s]))
            rows.append({'Parameter': label, 'Group/Session': cell_label(g, s),
                         'Mean': d['mean'], 'CI Lower': d['lo'], 'CI Upper': d['hi']})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- sources

def notebook_output(must_contain):
    nb = json.load(open(NOTEBOOK))
    cell = next(c for c in nb['cells'] if must_contain in ''.join(c['source']))
    return ''.join(cell['outputs'][-1]['data']['text/plain'])


def published_table():
    """The stored DataFrame output of the notebook cell that made the published table."""
    rows, param = [], None
    for line in notebook_output('results_list.append([param_name, key').splitlines():
        m = re.match(r'^(\S+)?\s+(Group \d, Session \d)\s+(\S+)\s+(\S+)\s+(\S+)$', line)
        if m:
            param = m.group(1) or param
            rows.append({'Parameter': dict((v, l) for v, l in PARAMS)[param],
                         'Group/Session': m.group(2), 'Mean': float(m.group(3)),
                         'CI Lower': float(m.group(4)), 'CI Upper': float(m.group(5))})
    return pd.DataFrame(rows)


def published_table_s2():
    rows, param = [], None
    for line in notebook_output("for regressor in ['session', 'session:group']").splitlines():
        m = re.match(r'^(\S+)?\s+(session(?::group)?)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$', line)
        if m:
            param = m.group(1) or param
            rows.append(dict(var=param, regressor=m.group(2), p=m.group(3), mean=m.group(4),
                             lo=m.group(5), hi=m.group(6)))
    return rows


def main_text_effects():
    """The seven PMC regression effects in the Results paragraph, as printed."""
    text = subprocess.run(['pdftotext', '-layout', PAPER_PDF, '-'], capture_output=True,
                          text=True, check=True).stdout
    text = text[text.index('Our model-based analysis showed'):text.index('This is again')]
    text = re.sub(r'\s+', ' ', text)
    num = r'(-?\d*\.\d+)'
    stats = re.findall(rf'mean={num}, 95%CI\s?=\[{num}, {num}\]', text)
    ps = re.findall(rf'𝑝𝑏𝑎𝑦𝑒𝑠𝑖𝑎𝑛\s?={num}', text)
    # order of appearance in the paragraph: (label, variable, regressors summed)
    effects = [('Prior mean, group x session', 'prior_mu', ['session:group']),
               ('Prior mean, session effect in stress group', 'prior_mu', ['session', 'session:group']),
               ('Prior mean, session effect in control group', 'prior_mu', ['session']),
               ('Evidence SD option 1, group x session', 'n1_evidence_sd', ['session:group']),
               ('Evidence SD option 2, group x session', 'n2_evidence_sd', ['session:group']),
               ('Evidence SD option 1, session', 'n1_evidence_sd', ['session']),
               ('Evidence SD option 2, session', 'n2_evidence_sd', ['session'])]
    assert len(stats) == len(ps) == len(effects), (stats, ps)
    return [(*e, st, p) for e, st, p in zip(effects, stats, ps)]


def agrees(reported, value):
    """Equal up to the rounding of the printed number."""
    decimals = len(reported.split('.')[1])
    return abs(float(reported) - value) <= 0.5 * 10 ** -decimals + 1e-9


# --------------------------------------------------------------------------- output

def fmt(df, decimals=6):
    out = df.copy()
    for c in ['Mean', 'CI Lower', 'CI Upper']:
        out[c] = out[c].map(lambda v: f'{v:.{decimals}f}')
    return out


def to_markdown(df):
    lines = ['| ' + ' | '.join(df.columns) + ' |', '| ' + ' | '.join([':-:'] * df.shape[1]) + ' |']
    lines += ['| ' + ' | '.join(str(v) for v in row) + ' |' for row in df.itertuples(index=False)]
    return '\n'.join(lines)


def main(bids_folder):
    idata = az.from_netcdf(op.join(bids_folder, 'derivatives', 'cogmodels', 'model-5_trace.netcdf'))
    post, const = idata.posterior, idata.constant_data
    checks = ['# Supplementary Table 1: checks', '',
              f'Trace: `{op.join(bids_folder, "derivatives/cogmodels/model-5_trace.netcdf")}`, '
              f'{post.sizes["chain"]} chains x {post.sizes["draw"]} draws.', '']
    ok = True

    def check(passed, msg):
        nonlocal ok
        ok &= bool(passed)
        checks.append(f'- [{"x" if passed else " "}] {msg}')

    # 1. how was session coded in the fit? ------------------------------------------------
    checks += ['## 1. Session coding in the fitted design matrices', '']
    group_file = pd.read_csv(op.join(bids_folder, 'group_assignmentList.csv'), index_col='subject')['group']
    subj = post.subject.values[const['subject_ix'].values]
    for var, _ in PARAMS + [('prior_mu', 'prior_mu')]:
        names = regressors(post, var)
        if 'session' not in names:
            continue
        dm = pd.DataFrame(const[f'_dm_{var}'].values, columns=names)
        uniq = sorted(map(tuple, dm.drop_duplicates().values))
        check(set(dm['session']) == {1., 2.}
              and np.array_equal(dm['session:group'], dm['session'] * dm['group'])
              and np.array_equal(dm['group'], group_file.loc[subj].values),
              f'`_dm_{var}` {names}: unique rows {uniq}; session in {{1, 2}}, '
              f'session:group = session*group, group = group_assignmentList.csv (1 = stress)')

    # 2. the table ------------------------------------------------------------------------
    new = make_table(post, {1: 1., 2: 2.})
    old_recomputed = make_table(post, {1: 0., 2: 1.})
    old = published_table()

    new.to_csv(op.join(HERE, 'supp_table1.csv'), index=False)
    with open(op.join(HERE, 'supp_table1.md'), 'w') as f:
        f.write(CAPTION + '\n\n' + to_markdown(fmt(new)) + '\n')

    checks += ['', '## 2. Old table', '']
    key = ['Parameter', 'Group/Session']
    stat = ['Mean', 'CI Lower', 'CI Upper']
    m = old.merge(old_recomputed, on=key, suffixes=('', '_re'))
    check(len(old) == 24 and np.allclose(m[stat].values, m[[c + '_re' for c in stat]].values, atol=5e-7),
          'Published table (stored notebook output, 24 rows) is reproduced exactly by evaluating '
          'the trace with session coded 0/1')
    shifted = old[old['Group/Session'].str.endswith('Session 2')].assign(
        **{'Group/Session': lambda d: d['Group/Session'].str.replace('Session 2', 'Session 1')})
    m = shifted.merge(new, on=key, suffixes=('', '_new'))
    check(np.allclose(m[stat].values, m[[c + '_new' for c in stat]].values, atol=5e-7),
          'Old "Session 2" rows equal the corrected "Session 1" rows (one-step displacement)')

    diff = old.merge(new, on=key, suffixes=(' (old)', ' (new)'))
    for c in stat:
        diff[f'{c} (new - old)'] = diff[f'{c} (new)'] - diff[f'{c} (old)']
    diff.to_csv(op.join(HERE, 'supp_table1_diff.csv'), index=False)
    dshow = diff[key + ['Mean (old)', 'Mean (new)', 'Mean (new - old)',
                        'CI Lower (old)', 'CI Lower (new)', 'CI Upper (old)', 'CI Upper (new)']].copy()
    for c in dshow.columns[2:]:
        dshow[c] = dshow[c].map(lambda v: f'{v:+.3f}' if 'new - old' in c else f'{v:.3f}')
    with open(op.join(HERE, 'supp_table1_diff.md'), 'w') as f:
        f.write('# Supplementary Table 1: old (session coded 0/1) vs corrected (1/2)\n\n'
                'Old "Session 2" = new "Session 1"; old "Session 1" was an extrapolation to a '
                'session 0. Session-2 rows change by one further session step.\n\n'
                + to_markdown(dshow) + '\n')

    # 3. session-1 group differences -------------------------------------------------------
    checks += ['', '## 3. Session-1 group difference (stress - control), table scale', '']
    gap_rows = []
    for var, label in PARAMS:
        d = summarise(cell_draws(post, var, 1, 1.) - cell_draws(post, var, 0, 1.))
        gap_rows.append({'Parameter': label, **d, 'credible': not d['lo'] < 0 < d['hi']})
    gaps = pd.DataFrame(gap_rows)
    checks.append(to_markdown(gaps.assign(
        **{c: gaps[c].map(lambda v: f'{v:+.3f}') for c in ['mean', 'lo', 'hi']},
        p_pos=gaps.p_pos.map(lambda v: f'{v:.3f}')).rename(
        columns={'mean': 'Mean', 'lo': 'CI Lower', 'hi': 'CI Upper', 'p_pos': 'P(>0)'})))
    checks.append('')
    check(not gaps.credible.any(), 'No parameter differs credibly between groups at session 1 '
                                   '(every 95% CI contains 0)')
    ref = pd.read_csv(BASELINE_CSV).query("parameter == 'risky_prior_mu' and level == 'population'").iloc[0]
    mu = gaps.set_index('Parameter').loc['risky_prior_mu']
    check(all(f'{a:.3f}' == f'{b:.3f}' for a, b in zip(mu[['mean', 'lo', 'hi']], ref[['mean', 'lo', 'hi']])),
          f'Prior-mean gap {mu["mean"]:+.3f} [{mu["lo"]:+.3f}, {mu["hi"]:+.3f}] matches '
          f'rebuttal_baseline_contrasts.csv {ref["mean"]:+.3f} [{ref["lo"]:+.3f}, {ref["hi"]:+.3f}]')

    # 4. main-text effects --------------------------------------------------------------------
    checks += ['', '## 4. Group x session effects reported in the main text (coefficient scale)', '',
               'Reported values parsed from the submitted manuscript PDF. p_bayes in the paper '
               'is P(<0) for some effects and P(>0) for others; both are shown.', '',
               '| Effect | Reported mean [95% CI], p | Trace mean [95% CI] | P(>0) | P(<0) | Match |',
               '| :-- | :-- | :-- | :-: | :-: | :-: |']
    main_ok = True
    if not op.exists(PAPER_PDF):
        checks.append(f'| Skipped: `{op.relpath(PAPER_PDF, REPO)}` not present | | | | | |')
    for label, var, regs, (r_mean, r_lo, r_hi), r_p in (main_text_effects() if op.exists(PAPER_PDF) else []):
        names = regressors(post, var)
        x = coefs(post, var)[:, [names.index(r) for r in regs]].sum(1)
        d = summarise(x)
        match = (agrees(r_mean, d['mean']) and agrees(r_lo, d['lo']) and agrees(r_hi, d['hi'])
                 and (agrees(r_p, d['p_pos']) or agrees(r_p, 1 - d['p_pos'])))
        main_ok &= match
        checks.append(f'| {label} | {r_mean} [{r_lo}, {r_hi}], {r_p} | {d["mean"]:+.3f} '
                      f'[{d["lo"]:+.3f}, {d["hi"]:+.3f}] | {d["p_pos"]:.3f} | {1 - d["p_pos"]:.3f} | '
                      f'{"yes" if match else "NO"} |')
    checks.append('')
    if op.exists(PAPER_PDF):
        check(main_ok, 'All seven main-text effects reproduced from the trace (to the printed precision)')

    checks += ['', '## 5. Supplementary Table 2 (prior widths, coefficient scale)', '']
    s2_ok = True
    for r in published_table_s2():
        x = coefs(post, r['var'])[:, regressors(post, r['var']).index(r['regressor'])]
        d = summarise(x)
        s2_ok &= all(agrees(r[k], d[v]) for k, v in [('p', 'p_pos'), ('mean', 'mean'), ('lo', 'lo'), ('hi', 'hi')])
    check(s2_ok, 'Supplementary Table 2 (session and session:group on prior SDs) reproduced; '
                 'it reports coefficients only and needs no correction')

    checks += ['', f'**{"ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED"}**', '']
    with open(op.join(HERE, 'supp_table1_checks.md'), 'w') as f:
        f.write('\n'.join(checks))
    print('\n'.join(checks))
    return ok


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--bids_folder', default='/Users/gdehol/data/ds-stressrisk')
    raise SystemExit(0 if main(parser.parse_args().bids_folder) else 1)
