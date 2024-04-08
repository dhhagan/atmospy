"""Test the atmospy utility functions."""
import tempfile
from urllib.request import urlopen
from http.client import HTTPException

import pytest
import pandas as pd
from pandas.testing import (
    assert_series_equal,
    assert_frame_equal,
)
from atmospy.utils import (
    get_dataset_names,
    load_dataset,
    DATASET_NAMES_URL
)

def _network(t=None, url="https://github.com"):
    """_summary_

    Parameters
    ----------
    t : _type_, optional
        _description_, by default None
    url : str, optional
        _description_, by default "https://github.com"
    """
    if t is None:
        return lambda x: _network(x, url=url)
    
    def wrapper(*args, **kwargs):
        try:
            f = urlopen(url)
        except (OSError, HTTPException):
            pytest.skip("No internet connection.")
        else:
            f.close()
            return t(*args, **kwargs)
        
    return wrapper


def check_load_dataset(name):
    dataset = load_dataset(name, cache=False)
    assert isinstance(dataset, pd.DataFrame)

def check_load_cached_dataset(name):
    with tempfile.TemporaryDirectory() as tmpdir:
        dataset = load_dataset(name, cache=True, data_home=tmpdir)
        
        cached_dataset = load_dataset(name, cache=True, data_home=tmpdir)
        
        assert_frame_equal(dataset, cached_dataset)
        
@_network(url=DATASET_NAMES_URL)
def test_get_dataset_names():
    names = get_dataset_names()
    assert names
    assert "us-ozone" in names
    
@_network(url=DATASET_NAMES_URL)
def test_load_datasets():
    for name in get_dataset_names():
        check_load_dataset(name)
        
@_network(url=DATASET_NAMES_URL)
def test_load_cached_dataset_names():
    for name in get_dataset_names():
        check_load_cached_dataset(name)
        
@_network(url=DATASET_NAMES_URL)
def test_load_dataset_string_error():
    name = "invalid_name"
    with pytest.raises(ValueError):
        load_dataset(name)
        
@_network(url=DATASET_NAMES_URL)
def test_load_dataset_type_error():
    name = pd.DataFrame()
    
    with pytest.raises(TypeError):
        load_dataset(name)