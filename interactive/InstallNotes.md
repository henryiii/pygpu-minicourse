# Building the shared course environment on Adroit

These are the steps used to build the environment that the
`course/pygpu/default` module points at. Students do not need any of this.

The environment has to live in `base`, because that is what the modulefile ties
to.

```bash
cd /opt/export/course/pygpu
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
./bin/micromamba create -f environment.yml -r ./miniconda -n base
```

To update in place for a new term, use the same `environment.yml`:

```bash
cd /opt/export/course/pygpu
./bin/micromamba install -f environment.yml -r ./miniconda -n base
```

`environment.yml` here is a symlink to the one in the repository root, so the
shared environment and a local install stay in step.

Then check that the modulefile (`course.pygpu.default`) still points at the
right prefix.

## History

Earlier versions used a Miniconda or Mambaforge installer, given the
`/opt/export/course/pygpu/miniconda` path and answered "no" when it offered to
set up the `conda` command, followed by
`mamba env update -f environment.yml -n base`. JupyterLab extensions also had to
be built with `jupyter labextension install`; that is no longer needed, because
extensions are prebuilt and arrive with the environment.
