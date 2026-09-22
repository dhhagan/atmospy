"""Test the atmospy utility functions."""
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from atmospy.utils import (
    check_for_numeric_cols,
    check_for_timestamp_col,
    get_data_home,
    get_dataset_names,
    load_dataset,
    remove_na,
)


def test_get_data_home_explicit_path(tmp_path):
    target = tmp_path / "cache"

    assert get_data_home(target) == str(target)
    assert target.is_dir()


def test_get_data_home_from_environment(tmp_path, monkeypatch):
    target = tmp_path / "env-cache"
    monkeypatch.setenv("ATMOSPY_DATA", str(target))

    assert get_data_home() == str(target)
    assert target.is_dir()


def test_check_for_timestamp_col(hourly):
    check_for_timestamp_col(hourly, "timestamp")

    with pytest.raises(TypeError):
        check_for_timestamp_col(hourly, "pm25")


def test_check_for_numeric_cols(hourly):
    check_for_numeric_cols(hourly, ["pm25", "ws", "wd"])

    with pytest.raises(TypeError):
        check_for_numeric_cols(hourly, ["pm25", "timestamp"])


def test_load_dataset_rejects_non_string():
    with pytest.raises(TypeError):
        load_dataset(pd.DataFrame())


def test_remove_na_not_implemented():
    with pytest.raises(NotImplementedError):
        remove_na([1.0, None])


@pytest.mark.network
def test_get_dataset_names():
    names = get_dataset_names()

    assert names
    assert "us-ozone" in names


@pytest.mark.network
def test_load_datasets():
    for name in get_dataset_names():
        df = load_dataset(name, cache=False)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty


@pytest.mark.network
def test_load_cached_datasets(tmp_path):
    for name in get_dataset_names():
        df = load_dataset(name, cache=True, data_home=tmp_path)
        cached = load_dataset(name, cache=True, data_home=tmp_path)

        assert (tmp_path / f"{name}.csv").is_file()
        assert_frame_equal(df, cached)


@pytest.mark.network
def test_load_dataset_rejects_unknown_name():
    with pytest.raises(ValueError):
        load_dataset("invalid_name")
