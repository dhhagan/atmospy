# atmospy: air quality data visualization


[![PyPI version](https://badge.fury.io/py/atmospy.svg)](https://badge.fury.io/py/atmospy)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/atmospy)
[![Tests](https://github.com/dhhagan/atmospy/actions/workflows/tests.yml/badge.svg)](https://github.com/dhhagan/atmospy/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/dhhagan/atmospy/branch/main/graph/badge.svg)](https://codecov.io/gh/dhhagan/atmospy)
![Apache 2.0 licensed](https://img.shields.io/github/license/dhhagan/atmospy)


**atmospy** is a Python visualization library based on matplotlib and seaborn. 

## Documentation

Documentation for **atmospy** can be found [here](https://dhhagan.github.io/atmospy/index.html).

## Dependencies

### Supported Python versions

**atmospy** supports Python 3.10 and newer.

### Mandatory dependencies

  * numpy
  * pandas
  * seaborn
  * matplotlib
  * scipy

## Installation

The latest release can be installed directly from PyPi:

```sh
$ pip install atmospy
```

You can also install pre-releases from GitHub:

```sh
$ pip install atmospy --pre
```

If you would like to install from a specific branch or release, you can do so directly from GitHub:


```sh
$ pip install git+https://github.com/dhhagan/atmospy.git@<tag-or-version>
```

## Development

**atmospy** development takes place on GitHub: https://github.com/dhhagan/atmospy

The project is managed with [uv](https://docs.astral.sh/uv/). To set up a development environment, clone the repository and run:

```sh
$ uv sync
```

This creates a virtual environment in `.venv` and installs **atmospy** in editable mode along with the test dependencies. To build the documentation locally, include the docs dependency group as well:

```sh
$ uv sync --group docs
```

### Testing

Run the test suite with:

```sh
$ uv run pytest
```

Please submit bugs that you encounter to the [issue tracker](https://github.com/dhhagan/atmospy/issues) with a reproducible example that clearly demonstrates the problem.