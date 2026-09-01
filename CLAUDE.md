# Notes for Claude

Research repo (fMRI: stress & risky choice). Analysis code, not a software project —
no test suite, no CI, notebooks are the primary artefact.

## Read first

- `stress_risk/plots_for_paper/README.md` — what produced every paper figure and the
  full chain of scripts behind each input. **Read this before touching anything
  paper-related.**
- `stress_risk/ADDITIONAL_ANALYSES.md` — analyses that were run but not reported.
  Check here before re-implementing something; it has probably already been done.
- `stress_risk/DATA_ON_SHARE.md` — what lives on the department share and how to
  assemble a working data folder from it.
- `stress_risk/analysis_pipeline_StressRisk.md` — the real cluster/transfer commands.

## Environments — pick the right one, it matters

Two conda envs, and code fails in confusing ways in the wrong one:

- **`behav_fit`** (`/Users/mrenke/mambaforge/envs/behav_fit`) — bambi, bauer, arviz,
  pingouin. All behavioural model fitting and **all paper plotting notebooks**.
  Bar+swarm plots only align correctly here; PMC `model.ppc(...)` only runs here.
- **`numrefields`** — braincoder / TensorFlow. Encoding and decoding scripts.
  GPU cluster jobs additionally `source activate tf2-gpu`.

Never `pip install` into these to fix an import — ask first.

## Data lives outside the repo

Nothing in `~/data` or `/Volumes` is version-controlled, and paths are hard-coded
absolutes throughout (no config file).

- `/Users/mrenke/data/ds-stressrisk` — behaviour, `derivatives/cogmodels` (model
  traces), `interim_sum_data/` (the summary CSVs notebooks read).
- `/Volumes/mrenkeED/data/ds-stressrisk` — external drive: the large fMRI
  derivatives (GLM betas, encoding models, decoded PDFs). Often not mounted.
- `~/Desktop/StressRisk/...` — figure outputs and the cortisol file.

Analysis notebooks usually set both roots (`bids_folder` and `bids_folder_behav`).
Model traces are 300MB–1.2GB; **never add data files to git.**

## Gotchas

- **`utils.py` is four different modules.** `plots_for_paper/utils.py`,
  `behavior/utils.py`, `analyse_results/utils.py`, `fmri_analysis/*/utils.py` — all
  imported as a bare `from utils import ...`. Whichever directory is the working
  directory wins. Always run a notebook from its own directory.
- `stress_risk/utils/data.py` is the *package* module (`from stress_risk.utils.data
  import get_data`) — different thing again.
- Model labels: PMC model **`5`** is the paper model (common prior shift). Model `1`
  is the earlier risky/safe-separate version that several older analyses still use.
  Check which one a result came from before comparing numbers.
- `behavior/fit_bauerModels.py` unconditionally reads
  `interim_sum_data/r-prior-shift_Ediff_AUC.csv`, even for the paper models.
- Some committed code is out of date relative to what was actually run — e.g.
  `analyse_results/utils.py::get_stress_level` returns fewer columns than
  `paperFinal_supplements.ipynb` expects. Don't assume a notebook re-runs clean.

## Conventions

- Don't reformat or "tidy" notebooks that already ran — stored outputs are results.
  Editing a cell invalidates the output below it.
- Superseded work goes to an `archive/` subfolder with a README entry, not deleted.
- Prefer adding a new notebook over rewriting one that produced published numbers.
- Commit only when asked.
