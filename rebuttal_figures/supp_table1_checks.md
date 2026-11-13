# Supplementary Table 1: checks

Trace: `/Users/gdehol/data/ds-stressrisk/derivatives/cogmodels/model-5_trace.netcdf`, 4 chains x 1000 draws.

## 1. Session coding in the fitted design matrices

- [x] `_dm_n1_evidence_sd` ['Intercept', 'session', 'group', 'session:group']: unique rows [(1.0, 1.0, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0), (1.0, 2.0, 0.0, 0.0), (1.0, 2.0, 1.0, 2.0)]; session in {1, 2}, session:group = session*group, group = group_assignmentList.csv (1 = stress)
- [x] `_dm_n2_evidence_sd` ['Intercept', 'session', 'group', 'session:group']: unique rows [(1.0, 1.0, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0), (1.0, 2.0, 0.0, 0.0), (1.0, 2.0, 1.0, 2.0)]; session in {1, 2}, session:group = session*group, group = group_assignmentList.csv (1 = stress)
- [x] `_dm_risky_prior_std` ['Intercept', 'session', 'group', 'session:group']: unique rows [(1.0, 1.0, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0), (1.0, 2.0, 0.0, 0.0), (1.0, 2.0, 1.0, 2.0)]; session in {1, 2}, session:group = session*group, group = group_assignmentList.csv (1 = stress)
- [x] `_dm_safe_prior_std` ['Intercept', 'session', 'group', 'session:group']: unique rows [(1.0, 1.0, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0), (1.0, 2.0, 0.0, 0.0), (1.0, 2.0, 1.0, 2.0)]; session in {1, 2}, session:group = session*group, group = group_assignmentList.csv (1 = stress)
- [x] `_dm_prior_mu` ['session', 'group', 'session:group']: unique rows [(1.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 0.0, 0.0), (2.0, 1.0, 2.0)]; session in {1, 2}, session:group = session*group, group = group_assignmentList.csv (1 = stress)

## 2. Old table

- [x] Published table (stored notebook output, 24 rows) is reproduced exactly by evaluating the trace with session coded 0/1
- [x] Old "Session 2" rows equal the corrected "Session 1" rows (one-step displacement)

## 3. Session-1 group difference (stress - control), table scale

| Parameter | Mean | CI Lower | CI Upper | P(>0) | credible |
| :-: | :-: | :-: | :-: | :-: | :-: |
| risky_prior_mu | -0.013 | -0.415 | +0.389 | 0.475 | False |
| safe_prior_mu | -0.013 | -0.415 | +0.389 | 0.475 | False |
| n1_evidence_sd | +0.031 | -0.018 | +0.082 | 0.893 | False |
| n2_evidence_sd | +0.011 | -0.028 | +0.052 | 0.708 | False |
| risky_prior_sd | -0.000 | -0.127 | +0.130 | 0.494 | False |
| safe_prior_sd | +0.077 | -0.228 | +0.418 | 0.692 | False |

- [x] No parameter differs credibly between groups at session 1 (every 95% CI contains 0)
- [x] Prior-mean gap -0.013 [-0.415, +0.389] matches rebuttal_baseline_contrasts.csv -0.013 [-0.415, +0.389]

## 4. Group x session effects reported in the main text (coefficient scale)

Reported values parsed from the submitted manuscript PDF. p_bayes in the paper is P(<0) for some effects and P(>0) for others; both are shown.

| Effect | Reported mean [95% CI], p | Trace mean [95% CI] | P(>0) | P(<0) | Match |
| :-- | :-- | :-- | :-: | :-: | :-: |
| Prior mean, group x session | 0.51 [0.178, 0.852], 0.002 | +0.507 [+0.178, +0.852] | 0.998 | 0.002 | yes |
| Prior mean, session effect in stress group | 0.388 [0.084, 0.668], 0.009 | +0.388 [+0.084, +0.668] | 0.992 | 0.008 | yes |
| Prior mean, session effect in control group | -0.120 [-0.302, 0.07], 0.897 | -0.120 [-0.302, +0.070] | 0.103 | 0.897 | yes |
| Evidence SD option 1, group x session | 0.074 [-0.157, 0.299], 0.259 | +0.074 [-0.157, +0.299] | 0.742 | 0.258 | yes |
| Evidence SD option 2, group x session | -0.026 [-0.248, 0.197], 0.596 | -0.026 [-0.248, +0.197] | 0.404 | 0.596 | yes |
| Evidence SD option 1, session | -0.128 [-0.276, 0.022], 0.045 | -0.128 [-0.276, +0.022] | 0.045 | 0.955 | yes |
| Evidence SD option 2, session | -0.030 [-0.174, 0.111], 0.335 | -0.030 [-0.174, +0.111] | 0.335 | 0.665 | yes |

- [x] All seven main-text effects reproduced from the trace (to the printed precision)

## 5. Supplementary Table 2 (prior widths, coefficient scale)

- [x] Supplementary Table 2 (session and session:group on prior SDs) reproduced; it reports coefficients only and needs no correction

**ALL CHECKS PASSED**
