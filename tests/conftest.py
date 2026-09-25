"""Shared fixtures and configuration for the atmospy test suite.

Plotting and statistics tests run on small, deterministic synthetic datasets
so the default ``pytest`` run needs no network access. Tests that download
the example datasets are marked ``network`` and are skipped unless the run
is started with ``--run-network``.
"""
from urllib.request import urlopen

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from atmospy.utils import DATASET_NAMES_URL


def pytest_addoption(parser):
    parser.addoption(
        "--run-network",
        action="store_true",
        default=False,
        help="run tests that download the example datasets",
    )


def _have_network(url=DATASET_NAMES_URL, timeout=5):
    try:
        with urlopen(url, timeout=timeout):
            return True
    except OSError:
        return False


def pytest_collection_modifyitems(config, items):
    network_items = [item for item in items if "network" in item.keywords]
    if not network_items:
        return

    if not config.getoption("--run-network"):
        reason = "needs --run-network"
    elif not _have_network():
        reason = "no internet connection"
    else:
        return

    skip = pytest.mark.skip(reason=reason)
    for item in network_items:
        item.add_marker(skip)


@pytest.fixture(autouse=True)
def _close_figures():
    """Close every figure after each test so state never leaks between tests."""
    yield
    plt.close("all")


@pytest.fixture
def rng():
    return np.random.default_rng(20230101)


@pytest.fixture
def hourly(rng):
    """One calendar year (2023) of hourly pollutant and met data."""
    t = pd.date_range("2023-01-01", "2023-12-31 23:00", freq="h")
    return pd.DataFrame({
        "timestamp": t,
        "pm25": rng.gamma(shape=2.0, scale=6.0, size=t.size),
        "ws": rng.gamma(shape=2.0, scale=1.5, size=t.size),
        "wd": rng.uniform(0.0, 360.0, size=t.size),
    })


@pytest.fixture
def sensors(rng):
    """A reference measurement alongside three collocated sensors."""
    n = 500
    ref = rng.gamma(shape=2.0, scale=8.0, size=n)
    return pd.DataFrame({
        "Reference": ref,
        "Sensor A": 1.10 * ref + 0.5 + rng.normal(0.0, 1.0, size=n),
        "Sensor B": 0.95 * ref - 0.3 + rng.normal(0.0, 1.0, size=n),
        "Sensor C": 1.02 * ref + 0.1 + rng.normal(0.0, 1.0, size=n),
    })
