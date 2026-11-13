"""Fit the paper's probit (RNP) model with presentation order added.

Companion to `probit_order_interaction.ipynb`, which loads the traces written here.
Fits take 10-15 min each, so they live in a script that can run in parallel
instead of in the notebook.

Models (all: probit link, bernoulli, x = log(risky/safe)):

    paper     chose_risky ~ x*session*group + (x*session|subject)
              The paper model (bambi-RNP-fit_trace_model1), refit in the current
              bambi so the order model can be compared like-for-like.
    order     chose_risky ~ x*session*group*order + (x*session|subject)
              The requested model: random effects as in the paper model.
    order_re  chose_risky ~ x*session*group*order + (x*session*order|subject)
              Sensitivity check. Order varies within subject, so without by-subject
              order slopes the order interactions can be over-precise.

`session` is numeric 1/2 and `group` and `order` numeric 0/1 (order = 1 means risky
first), as in the paper model. The session:group... coefficients are therefore
per-unit-session differences, i.e. session 2 minus session 1.

Sampler settings are the paper notebook's: init='adapt_diag', target_accept=0.9,
1000 tune + 1000 draws, 4 chains, bambi default priors.

    python fit_probit_order.py order --bids_folder /Users/gdehol/data/ds-stressrisk
"""
import argparse
import os.path as op

import arviz as az
import bambi

from stress_risk.utils.data import BIDS_FOLDER, get_data

FORMULAE = {
    'paper': 'chose_risky ~ x*session*group + (x*session|subject)',
    'order': 'chose_risky ~ x*session*group*order + (x*session|subject)',
    'order_re': 'chose_risky ~ x*session*group*order + (x*session*order|subject)',
}


def trace_path(label, bids_folder=BIDS_FOLDER):
    return op.join(bids_folder, 'derivatives', 'cogmodels',
                   f'bambi-RNP-fit_trace_model-{label}.netcdf')


def get_model_data(bids_folder=BIDS_FOLDER):
    """Trial-level choices, flat (one row per trial), as the paper notebook uses them."""
    df = get_data(bids_folder=bids_folder).reset_index()
    df['group'] = df['group'].astype(int)
    df['x'] = df['log(risky/safe)']
    df['order'] = df['risky_first'].astype(int)
    return df


def build(label, df):
    return bambi.Model(FORMULAE[label], link='probit', family='bernoulli',
                       data=df)


def main(label, bids_folder, seed):
    df = get_model_data(bids_folder)
    model = build(label, df)
    print(model)
    traces = model.fit(init='adapt_diag', target_accept=0.9, draws=1000, tune=1000,
                       chains=4, cores=4, random_seed=seed,
                       idata_kwargs={'log_likelihood': True})
    fn = trace_path(label, bids_folder)
    az.to_netcdf(traces, fn)
    print(az.summary(traces, var_names=['~|subject'], filter_vars='like').to_string())
    print(f'saved {fn}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('label', choices=list(FORMULAE))
    parser.add_argument('--bids_folder', default=BIDS_FOLDER)
    parser.add_argument('--seed', type=int, default=1234)
    args = parser.parse_args()
    main(args.label, args.bids_folder, args.seed)
