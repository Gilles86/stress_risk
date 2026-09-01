# Notes for Claude

Research repo for the paper *Acute stress reduces risk-aversion by changing magnitude
perception* (fMRI, 2 sessions, MIST stress induction, numerosity-based risky choice).

Analysis code, not a software project — no test suite, no CI, notebooks are the
primary artefact and their stored outputs are results.

**Current state (September 2026): reviews are back.** Expect small follow-up
analyses rather than new pipeline work. Before building anything, check
`stress_risk/ADDITIONAL_ANALYSES.md` — 15 analyses were run and then cut from the
manuscript, so what a reviewer asks for has often already been done.

## Read first

| Document | For |
| --- | --- |
| `stress_risk/plots_for_paper/README.md` | Which notebook makes which figure/statistic, and the full chain of scripts behind every input it reads. **Read before touching anything paper-related.** |
| `stress_risk/ADDITIONAL_ANALYSES.md` | Analyses run but not reported. **Check here first when answering a reviewer.** |
| `stress_risk/DATA_ON_SHARE.md` | What is on the department share and how to assemble a working dataset from it. |
| `stress_risk/analysis_pipeline_StressRisk.md` | The real cluster/transfer commands, if the neural pipeline ever has to be rerun. |

## Setting up on a new machine

All absolute paths in this repo and in the docs are **Maike's** (`/Users/mrenke/...`).
Yours will differ. Two things to do:

1. **Get the data.** It is on the UZH econ department share; `DATA_ON_SHARE.md` has a
   two-line `rsync` that assembles a working `ds-stressrisk` folder. The paper
   figures need ~1.1 GB, the supplements ~3.5 GB. You do **not** need the imaging
   derivatives (hundreds of GB) unless you are rerunning the encoding/decoding
   pipeline — the decoding is already summarised into CSVs.

2. **Point the code at it.** One line, `stress_risk/utils/data.py`:

   ```python
   BIDS_FOLDER = '/Users/mrenke/data/ds-stressrisk'
   ```

   Every function in `utils/data.py`, `behavior/utils.py` and
   `analyse_results/utils.py` defaults to it and still accepts `bids_folder=`.
   The notebooks in `plots_for_paper/` set `bids_folder` in their first cell.
   Scripts take `--bids_folder`.

   Figure output paths (`plot_folder_path`, `supplements_path`) are still absolute
   and point at Maike's Desktop — change them or the `savefig` lines will fail.

## Environments — pick the right one, it matters

Two conda envs; code fails in confusing ways in the wrong one:

- **`behav_fit`** — bambi, bauer, arviz, pingouin. All behavioural model fitting and
  **all paper plotting notebooks**. Bar+swarm plots only align correctly here, and
  the PMC posterior predictive check (`model.ppc(...)`) only runs here.
- **`numrefields`** — braincoder / TensorFlow. Encoding and decoding scripts. GPU
  cluster jobs additionally `source activate tf2-gpu`.

Specs in `environments/`. Install the package itself with `pip install --editable .`
from the repo root. Never `pip install` into an existing env to fix an import — ask
the user first.

To run a notebook non-interactively (useful for producing a finished,
output-carrying notebook in one shot):

```bash
<env>/bin/jupyter nbconvert --to notebook --execute --inplace <nb>.ipynb
```

## Adding a new analysis

The pattern that fits this repo, and a worked example to copy:
`stress_risk/plots_for_paper/brainBehav_commonPriorShift_vs_neuralShift.ipynb`
(a reviewer-response analysis written this way).

- **New notebook, don't edit an existing one.** Never modify `paperFinal_*.ipynb` —
  their stored outputs are the numbers in the manuscript.
- Behaviour comes from `stress_risk.utils.data.get_data(bids_folder)`; group
  assignment from `get_group_mapping()` or `add_cond2df()`.
- Fitted models are in `derivatives/cogmodels/*.netcdf`, loaded with
  `az.from_netcdf`. Summary tables are in `interim_sum_data/` (flat).
- Record the result in `ADDITIONAL_ANALYSES.md` — that file is the index the next
  person searches.
- If it changes a paper number, say so loudly; otherwise it is an *additional*
  analysis and belongs in that index, not in the paper notebooks.

## Gotchas

- **`utils.py` names four different modules** — `plots_for_paper/utils.py`,
  `behavior/utils.py`, `analyse_results/utils.py`, `fmri_analysis/*/utils.py`, all
  imported as a bare `from utils import ...`. Whichever directory is the working
  directory wins, so **always run a notebook from its own directory**.
  `stress_risk/utils/data.py` is the installed package module
  (`from stress_risk.utils.data import ...`) — different thing again.
- **Model labels matter.** PMC model **`5`** is the paper model (risky and safe
  priors shift together). Model `1` is the earlier risky/safe-separate version that
  several older analyses still use, and the two give different answers — check which
  one a result came from before comparing numbers. Model `9` is *not* a common-prior
  model despite sounding like one, and has never been fit.
- **Two data roots in older notebooks.** Notebooks under `analyse_results/` set both
  `bids_folder` (external drive, large derivatives) and `bids_folder_behav`
  (local, behaviour + summary CSVs).
- `behavior/fit_bauerModels.py` reads `interim_sum_data/r-prior-shift_Ediff_AUC.csv`
  unconditionally, so that file must exist to refit *any* PMC model.
- Model traces are 300 MB – 1.2 GB. **Never add data files to git.**
- Not every notebook re-runs clean — some were run against newer local code than what
  was committed. Check `plots_for_paper/README.md` → *Rough edges* before assuming a
  failure is your fault.

## Conventions

- Don't reformat or "tidy" notebooks that already ran — stored outputs are results,
  and editing a cell invalidates everything below it.
- Exception: **strip outputs before committing a notebook whose output is a figure
  payload rather than a result.** A plotly figure embeds ~1.2 MB of mesh JSON per
  cell; `vis_nPRFmodel_3d.ipynb` reached 12 MB that way and broke `git push`
  (HTTP 400 — git's default 1 MB `http.postBuffer`; this clone sets it to 500 MB, a
  fresh clone will not). Commit the exported PDF/PNG next to the notebook instead.
  Does **not** apply to `paperFinal_*`.
- Superseded work goes to an `archive/` subfolder with a README entry, not deleted —
  cut analyses are exactly what review asks about.
- Commit only when asked. `main` is shared with the PI (`Gilles86/stress_risk`), so
  no history rewrites or force-pushes.
