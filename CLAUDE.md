# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Teaching material for "PyGPU: High performance Python for GPUs", a minicourse by
Henry Schreiner. The repository is a set of Jupyter notebooks, not a Python
package. There is no build step, no test suite, and no importable library
(`sbatch_magic.py` is an IPython extension, loaded from a notebook).

Students run it on the Princeton Adroit cluster through OnDemand JupyterLab. See
`README.md` for the student setup steps.

## Commands

- Lint and format: `prek -a --quiet`. This runs `ruff check --fix` and
  `ruff format` over the notebooks (configured in `ruff.toml`), `nbstripout`
  (all notebook outputs must stay empty in git), codespell, and prettier on
  YAML/Markdown.
- Local environment: `micromamba create -f environment.yml` (conda-forge only;
  needs an NVidia GPU and CUDA on Linux).
- To check a change to `environment.yml` without a GPU box, dry-run the solve
  for the cluster's platform:
  `CONDA_OVERRIDE_CUDA=12.9 CONDA_OVERRIDE_GLIBC=2.34 micromamba create -n t --platform linux-64 --dry-run -f environment.yml`
- Run one notebook on a GPU node: open `ExampleRunner.ipynb`, put the notebook
  base name (no extension) on the `%%sbatch` line, and run the cell.

## Architecture

### Notebook sequence

The number prefix is the teaching order. A letter suffix means the same problem
solved with a different library, so those notebooks are parallel, not
sequential:

- `00_intro` — slides only (GPU concepts, CUDA/ROCm/SYCL terms).
- `01a` / `01b` — Mandelbrot fractal in CuPy and in Numba CUDA.
- `02a` / `02b` / `02c` — unbinned negative log likelihood in CuPy,
  TensorFlow, and PyTorch. `02x_torch_autograd` is an aside on autograd.
- `03_nll` — combined CuPy + Numba version of the NLL problem.
- `04_ode` — an ODE solver that is _slower_ on the GPU; the counter-example.

Each library notebook keeps the same shape: a NumPy CPU baseline first, then the
GPU version, then `%%timeit` comparisons. Keep that shape when you edit or add
notebooks, and keep the CPU baseline honest.

### GPU job submission

Students edit on a CPU-only JupyterLab session and send each notebook to a
shared GPU one at a time. Two mechanisms exist for this:

- `sbatch_magic.py` — the current one. `%load_ext sbatch_magic` gives a
  `%%sbatch <name>` cell magic. The cell body is an sbatch script;
  `str.format` fills `{name}` and any global from the notebook. The magic writes
  `<name>.sbatch`, submits it, and streams `<name>.out` into a live display cell
  until it sees the `[SBATCH-DONE]` marker it appends, then deletes both files.
  The job runs `jupyter nbconvert --to html --execute`, so students read the
  result as `<name>.html`.
- `ExampleRunnerExample.ipynb` — the older, unpacked version of the same idea
  written out cell by cell (`%%writetemplate`, `!sbatch`, a blocking
  `watch_file`). It is kept as a teaching artifact. Do not "fix" it to match
  `sbatch_magic.py`; the point is that it shows the steps.

Both write generated `*.sbatch`, `*.out`, and `*.html` files into the repository
root. `.gitignore` covers them.

### Cluster setup files

`interactive/` holds files that live on Adroit, not on the student side:
the environment modulefile (`course.pygpu.default`, `default`), an sbatch script
for a port-forwarded interactive JupyterLab, and `InstallNotes.md`,
which is the record of how the shared `/opt/export/course/pygpu` micromamba
environment was built. `interactive/environment.yml` is a symlink to the root
one. Update the notes when the install procedure changes.

## Conventions

- The notebook kernel is the course kernel (`sys_pygpu201912`); leave the
  kernelspec metadata alone, or every notebook shows a diff.
- Notebooks carry a date and a survey link near the top of `00_intro`. These
  need an update for each new offering of the course.
- Numbers, GPU names, and library-version remarks in the prose are from a
  specific year's run. Do not treat them as current facts.
- The slurm reservation name changes each term. It appears in `README.md`,
  `ExampleRunner.ipynb`, and `ExampleRunnerExample.ipynb`; keep the three in
  step.

## Environment constraints

`environment.yml` pins Python 3.12 and `cuda-version` 12.9 because TensorFlow is
the last of the four GPU libraries to support a new release of either — it is
the binding constraint, and CuPy/PyTorch/numba-cuda would otherwise go to CUDA
13. Dropping `tensorflow-gpu` (and `02b_nll_tensorflow.ipynb`) is what unblocks
a Python or CUDA bump.

`numba` no longer contains the CUDA target; `numba-cuda` supplies the
`numba.cuda` namespace and must be installed alongside it.
