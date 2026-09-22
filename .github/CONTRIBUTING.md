Contributing to atmospy
=======================

Reporting bugs
--------------

If you think you've encountered a bug in atmospy, please report it on the [Github issue tracker](https://github.com/dhhagan/atmospy/issues/new). To be useful, bug reports must include the following information:

- A reproducible code example that demonstrates the problem
- The output that you are seeing (an image of a plot, or the error message)
- A clear explanation of why you think something is wrong
- The specific version of atmospy that you are working with

Bug reports are easiest to address if they can be demonstrated using one of the example datasets from the atmospy docs (i.e. with `atmospy.load_dataset`). Otherwise, it is preferable that your example generate synthetic data to reproduce the problem. If you can only demonstrate the issue with your actual dataset, you will need to share it, ideally as a csv. Note that you can upload a csv directly to a github issue thread, but it must have a `.txt` suffix.

If you've encountered an error, searching the specific text of the message before opening a new issue can often help you solve the problem quickly and avoid making a duplicate report.


New features
------------

If you think there is a new feature that should be added to atmospy, you can open an issue to discuss it.


Setting up a development environment
------------------------------------

atmospy uses [uv](https://docs.astral.sh/uv/) to manage its virtual environment, dependencies, and lock file. After cloning the repository, run:

```sh
uv sync
```

This creates `.venv`, installs atmospy in editable mode, and installs the test dependencies pinned in `uv.lock`. Run the tests with:

```sh
uv run pytest
```

To build the documentation locally you also need the `docs` dependency group and [pandoc](https://pandoc.org):

```sh
uv sync --group docs
cd docs
uv run make notebooks html
```

When you add or change a dependency, edit `pyproject.toml` (or use `uv add`) and commit the updated `uv.lock` alongside it. Continuous integration installs with `uv sync --locked`, so a stale lock file will fail the build.
