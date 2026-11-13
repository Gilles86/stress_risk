"""Shared loaders for the reviewer-response analyses (rebuttal 1).

Deliberately standalone: does not import stress_risk.utils.data, so it runs in any
env with pandas/arviz and does not depend on BIDS_FOLDER being repointed.

The design-matrix coding matters and is easy to get wrong: patsy sees `session` as
NUMERIC 1/2 and `group` as 0/1, so a per-cell parameter value is

    Intercept + s*b_session + g*b_group + s*g*b_session:group      s in {1,2}

Verified against the data with patsy, and confirmed by posterior-predictive
log-likelihood (1/2 coding beats 0/1 by ~1750 units).
"""
import os.path as op

import numpy as np
import pandas as pd

BIDS_FOLDER = '/Users/gdehol/data/ds-stressrisk'
COGMODELS = op.join(BIDS_FOLDER, 'derivatives', 'cogmodels')
TRACE = op.join(COGMODELS, 'model-5_trace.netcdf')
trace_path = lambda label: op.join(COGMODELS, f'model-{label}_trace.netcdf')
RISKY_P = 0.55

softplus = lambda x: np.log1p(np.exp(x))


def get_behavior(bids_folder=BIDS_FOLDER):
    """Trial-level behaviour, via the package's own data layer.

    Delegates to stress_risk.utils.data.get_all_behavior, which goes through
    Subject.get_behavior and builds exact BIDS filenames. Do NOT reimplement this
    with glob: '*_events.tsv' also matches '*_value_events.tsv', which holds the
    PMC's fitted percepts (n1_hat/n2_hat) rather than the presented payoffs, so a
    glob silently doubles every trial and corrupts every payoff-derived variable.
    That is exactly the bug this function exists to prevent (2026-09-02).

    Returns the columns _cleanup_behavior already derives - risky_first,
    chose_risky, n_risky, n_safe, frac, log(risky/safe) - plus flat subject /
    session / run / trial_nr / group columns.
    """
    from stress_risk.utils.data import get_all_behavior

    df = get_all_behavior(bids_folder=bids_folder, drop_no_responses=False)
    df = df.reset_index()
    df['group'] = df.group.astype(int)
    return df


def design(session, group, regressors):
    """Row of the fitted design matrix, by REGRESSOR NAME, at numeric session 1/2.

    Reading the names off the trace rather than assuming a column order keeps this
    correct for models whose regressors differ (model 5's shared `prior_mu` has no
    intercept; model 1's option-specific prior means do).
    """
    if isinstance(regressors, bool):     # legacy call: an intercept FLAG, not names
        regressors = (['Intercept'] if regressors else []) + ['session', 'group',
                                                             'session:group']
    s, g = float(session), float(group)
    col = {'Intercept': 1., 'session': s, 'group': g, 'session:group': s * g}
    return np.array([col[str(r)] for r in regressors])


class PMCParams:
    """Per-cell PMC parameters from a fitted trace, group- or subject-level.

    Handles both parameterisations:
      * model 5  - one shared prior-mean shift (`prior_mu`) added to option-specific
                   intercepts, so the risky and safe prior means move together;
      * model 1  - `risky_prior_mu` and `safe_prior_mu` each carry their own
                   session*group regression and are free to move apart.
    Which one is in the trace is detected from its variables.
    """

    def __init__(self, trace=TRACE):
        import arviz as az
        self.post = az.from_netcdf(trace).posterior
        self.subjects = list(self.post.subject.values)
        self.shared_prior_shift = 'prior_mu_mu' in self.post
        self.label = op.basename(trace).split('_')[0]

    def regressors(self, var):
        return list(self.post[f'{var}_mu'].coords[f'{var}_regressors'].values)

    def draws(self, var, subject=None):
        """(draw, regressor) array; group level unless `subject` is given."""
        v = var if subject is not None else var + '_mu'
        d = self.post[v]
        if subject is not None:
            d = d.sel(subject=subject)
        return d.stack(s=('chain', 'draw')).transpose('s', ...).values

    def value(self, var, session, group, subject=None):
        """Posterior draws of `var` in cell (session, group), untransformed."""
        X = design(session, group, self.regressors(var))
        return self.draws(var, subject) @ X

    def cell(self, session, group, subject=None):
        """The six quantities the PMC decision rule needs, softplus applied."""
        v = lambda p: self.value(p, session, group, subject)
        mu_risky, mu_safe = v('risky_prior_mu'), v('safe_prior_mu')
        if self.shared_prior_shift:
            shift = v('prior_mu')
            mu_risky, mu_safe = mu_risky + shift, mu_safe + shift
        return dict(
            nu1=softplus(v('n1_evidence_sd')), nu2=softplus(v('n2_evidence_sd')),
            sd_risky=softplus(v('risky_prior_std')), sd_safe=softplus(v('safe_prior_std')),
            mu_risky=mu_risky, mu_safe=mu_safe)


def weight(prior_sd, evidence_sd):
    """Weight on the evidence in the posterior mean: w = s^2 / (s^2 + nu^2)."""
    return prior_sd ** 2 / (prior_sd ** 2 + evidence_sd ** 2)


def perceived_ev(payoff, p, prior_mu, prior_sd, evidence_sd):
    """Perceived expected value of an option, in natural (CHF/coin) units."""
    w = weight(prior_sd, evidence_sd)
    return p * np.exp(w * np.log(payoff) + (1 - w) * prior_mu)


def load_decoded(bids_folder=BIDS_FOLDER):
    """Within- and across-session decoded posteriors, deduplicated.

    within_ses_decodedE.csv ships with 11666 exactly-duplicated rows and carries no
    option identity; across_ses_decodedE.csv is clean and carries n1/risky_first.
    """
    p = op.join(bids_folder, 'interim_sum_data')
    within = (pd.read_csv(op.join(p, 'within_ses_decodedE.csv'))
                .drop_duplicates(['subject', 'session', 'trial_nr']))
    across = pd.read_csv(op.join(p, 'across_ses_decodedE.csv'))
    return within, across
