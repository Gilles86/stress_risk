# Acute stress reduces risk-aversion by changing magnitude perception

This Github repo contains all the code that has been used for the paper 'Acute stress reduces risk-aversion by changing magnitude perception'

The preprint can be found here:
https://www.biorxiv.org/content/10.1101/2025.11.03.685504v1.full.pdf

## Installation

Clone this git repository

git clone https://github.com/Gilles86/stress_risk.git

install the analysis package (editable) from the repo root:
`pip install --editable .`

Conda environments are in `environments/`; see `CLAUDE.md` for which one to use.

## Usage

* code that was used to present the main experiment to participants can be found in `experiment`
* code for the stress task in `fMRIMIST`
* all analysis code (behavior & neural) can be found in `stress_risk`
* reviewer-response analyses (first revision): `stress_risk/rebuttal1/`, `rebuttal_figures/`, `notes/rebuttal1/`
* superseded material kept for the record: `archive/` (and `archive/` subfolders inside `stress_risk/`)

## Where to find what

| Document | Covers |
| --- | --- |
| [`stress_risk/plots_for_paper/README.md`](stress_risk/plots_for_paper/README.md) | **Start here for the paper.** Which notebook makes which figure/statistic, and the full chain of scripts that produced every input it reads. |
| [`stress_risk/ADDITIONAL_ANALYSES.md`](stress_risk/ADDITIONAL_ANALYSES.md) | Analyses that were run but not reported — ROI controls, brain–behaviour correlations, motion controls, model variants. For reviewer questions. |
| [`stress_risk/DATA_ON_SHARE.md`](stress_risk/DATA_ON_SHARE.md) | Where the data lives on the department share, how to assemble a working `ds-stressrisk` folder from it, and the minimum file set per paper notebook. |
| [`stress_risk/analysis_pipeline_StressRisk.md`](stress_risk/analysis_pipeline_StressRisk.md) | Operational log: the actual data-transfer, fMRIPrep, MRIQC and cluster commands, with the subject lists. |
| [`stress_risk/rebuttal1/README.md`](stress_risk/rebuttal1/README.md) | Index of the reviewer-response analyses (first revision), including the corrected Supplementary Table 1 in [`rebuttal_figures/`](rebuttal_figures/). |
| [`archive/README.md`](archive/README.md) | What was moved out of the way and why. |

## Further info

The project heavily builds upon the following two packages

* braincoder (https://braincoder-devs.github.io)
* bauer (https://github.com/ruffgroup/bauer/tree/main)
