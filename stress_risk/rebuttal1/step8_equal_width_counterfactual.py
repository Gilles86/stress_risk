"""R1.1: is the prior-width asymmetry NECESSARY for a common prior shift to raise risk-seeking?

Counterfactual on the fitted model. Take the stress group's session-1 parameters
(group level), apply ONLY the fitted session-2 shift in the shared prior mean, and
compute the change in P(chose risky) over the trials the stress group actually saw.
Repeat with the two prior widths replaced by equal values, and with them swapped.

Why the widths matter: the decision variable is
    w_r log r + (1 - w_r) mu_r + log p - w_s log s - (1 - w_s) mu_s,
so a shared shift d moves it by (w_s - w_r) d. With equal prior widths w differs
only by presentation POSITION (nu1 != nu2), so the shift pushes towards risky in one
order and towards safe in the other, and cancels over the counterbalanced orders.

Choice rule as in the bauer version model 5 was fitted with (maike branch,
core._get_choice_predictions): the decision noise is the combined POSTERIOR sd,
    sd_k = sqrt(sigma_k^2 nu_k^2 / (sigma_k^2 + nu_k^2)),  P(risky) = Phi(DV / sqrt(sd_1^2 + sd_2^2)).
Verified: this reproduces the trace's stored trialwise `p` to 4e-9. (Current bauer's
default, sqrt(nu1^2 + nu2^2), does NOT, and was used by an earlier draft of this file.)

Also reports, for scale, the change predicted by the full model (every parameter at
its session-2 value).

Writes notes/rebuttal1/results/equal_width_counterfactual.csv.
"""
import os.path as op
import sys

import numpy as np
import pandas as pd
from scipy.stats import norm

sys.path.insert(0, op.dirname(op.abspath(__file__)))
from common import PMCParams, RISKY_P, get_behavior, weight  # noqa: E402

OUT = '/Users/gdehol/git/stress_risk/notes/rebuttal1/results'
N_DRAWS = 1000


def p_risky(c, R, S, rf, sd_r, sd_s, shift=0.):
    """(draw x trial) P(chose risky). rf: bool array, risky presented first."""
    nu_r = np.where(rf[None, :], c['nu1'][:, None], c['nu2'][:, None])
    nu_s = np.where(rf[None, :], c['nu2'][:, None], c['nu1'][:, None])
    wr, ws = weight(sd_r[:, None], nu_r), weight(sd_s[:, None], nu_s)
    er = wr * np.log(R) + (1 - wr) * (c['mu_risky'] + shift)[:, None]
    es = ws * np.log(S) + (1 - ws) * (c['mu_safe'] + shift)[:, None]
    dv = er + np.log(RISKY_P) - es
    post_var = lambda sd, nu: sd[:, None] ** 2 * nu ** 2 / (sd[:, None] ** 2 + nu ** 2)
    return norm.cdf(dv / np.sqrt(post_var(sd_r, nu_r) + post_var(sd_s, nu_s)))


def thin(c, ix):
    return {k: v[ix] for k, v in c.items()}


def run():
    P = PMCParams()
    df = get_behavior()
    df = df[df.group == 1]                          # the trials the stress group saw
    R, S = df.n_risky.values.astype(float), df.n_safe.values.astype(float)
    rf = df.risky_first.values.astype(bool)

    c1, c2 = P.cell(1, 1), P.cell(2, 1)
    ix = np.random.default_rng(1).choice(len(c1['nu1']), N_DRAWS, replace=False)
    c1, c2 = thin(c1, ix), thin(c2, ix)
    shift = c2['mu_risky'] - c1['mu_risky']        # shared prior-mean shift (per draw)
    sr, ss = c1['sd_risky'], c1['sd_safe']
    g = np.sqrt(sr * ss)

    scenarios = [('Fitted', sr, ss), ('Equal (risky width)', sr, sr),
                 ('Equal (geometric mean)', g, g), ('Equal (safe width)', ss, ss),
                 ('Swapped', ss, sr)]
    rows = []

    def add(name, d_trial):
        # d_trial: (draw x trial) change in P(risky)
        for order, m in (('Risky first', rf), ('Safe first', ~rf)):
            v = 100 * d_trial[:, m].mean(1)
            rows.append(dict(scenario=name, order=order, mean=v.mean(),
                             lo=np.percentile(v, 2.5), hi=np.percentile(v, 97.5),
                             p_gt0=np.mean(v > 0)))
        v = 100 * (d_trial[:, rf].mean(1) + d_trial[:, ~rf].mean(1)) / 2
        rows.append(dict(scenario=name, order='Average', mean=v.mean(),
                         lo=np.percentile(v, 2.5), hi=np.percentile(v, 97.5),
                         p_gt0=np.mean(v > 0)))

    for name, a, b in scenarios:
        add(name, p_risky(c1, R, S, rf, a, b, shift) - p_risky(c1, R, S, rf, a, b))
    add('Full model', p_risky(c2, R, S, rf, c2['sd_risky'], c2['sd_safe'])
        - p_risky(c1, R, S, rf, sr, ss))

    out = pd.DataFrame(rows)
    out.to_csv(op.join(OUT, 'equal_width_counterfactual.csv'), index=False)
    return out


if __name__ == '__main__':
    out = run()
    print(f'stress group, {N_DRAWS} draws; change in P(chose risky), percentage points\n')
    print(out.round(2).to_string(index=False))
