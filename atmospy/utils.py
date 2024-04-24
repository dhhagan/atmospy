"""Utility functions for internal use."""

import os
from urllib.request import (
    urlopen,
    urlretrieve
)
from seaborn.external.appdirs import (
    user_cache_dir,
)
import pandas as pd

DATASET_SOURCE = "https://raw.githubusercontent.com/dhhagan/atmospy-data/main"
DATASET_NAMES_URL = f"{DATASET_SOURCE}/dataset_names.txt"

def get_dataset_names():
    """List the avaiable sample datasets.
    
    Requires an internet connection.
    """
    with urlopen(DATASET_NAMES_URL) as resp:
        txt = resp.read()
        
    dataset_names = [name.strip() for name in txt.decode().split("\n")]
        
    return list(filter(None, dataset_names))

def get_data_home(data_home=None):
    """Return a path to the cache directory for the sample datasets.

    If the ``data_home`` argument is not provided and the `ATMOSPY_DATA` 
    environment variable is not set, an OS-appropriate folder will be created 
    and used.
    
    Parameters
    ----------
    data_home : Path, optional
        A path to store cached datasets, by default None
    """
    if data_home is None:
        data_home = os.environ.get("ATMOSPY_DATA", user_cache_dir("atmospy"))
    
    data_home = os.path.expanduser(data_home)
    if not os.path.exists(data_home):
        os.makedirs(data_home)
    
    return data_home

def load_dataset(name, cache=True, data_home=None, **kwargs):
    """Load an example dataset from the online repository.
    
    TODO: Add proper docs.

    Parameters
    ----------
    name : _type_
        _description_
    cache : bool, optional
        _description_, by default True
    data_home : _type_, optional
        _description_, by default None
        
    Returns
    -------
    df : :classL`pandas.DataFrame`
        Tabular data.
    
    """
    if not isinstance(name, str):
        err = (
            "This function only accepts strings and the string must be one of the example datasets.",
        )
        raise TypeError(err)
    
    available_dataset_names = get_dataset_names()
    if name not in available_dataset_names:
        raise ValueError(f"{name} is not a valid option. Please choose one of {available_dataset_names}.")
    
    url = f"{DATASET_SOURCE}/{name}.csv"
    
    if cache:
        cache_path = os.path.join(get_data_home(data_home), os.path.basename(url))
        
        # Check for the existence of a locally cached version
        if not os.path.exists(cache_path):
            urlretrieve(url, cache_path)
            
        full_path = cache_path
    else:
        full_path = url
        
    # Load the data into a DataFrame
    df = pd.read_csv(full_path, **kwargs)
    
    # Here is where we can/should place any dataset-dependent modifications
    if name == "us-ozone":
        df["Timestamp GMT"] = pd.to_datetime(df["Timestamp GMT"])
        
    if name == "us-bc":
        df["Timestamp GMT"] = pd.to_datetime(df["Timestamp GMT"])
        
    if name == "air-sensors-pm":
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    if name == "air-sensors-met":
        df["timestamp_local"] = pd.to_datetime(df["timestamp_local"])
    
    return df

def remove_na(vec):
    return

def check_for_timestamp_col(data, col):
    """Make sure the column is a proper timestamp according to Pandas.

    Parameters
    ----------
    data : pd.DataFrame
        Tabular data containing `col`.
    col : str
        The name of the column to check.
    """
    if not pd.core.dtypes.common.is_datetime64_any_dtype(data[col]):
        raise TypeError(f"Column `{col}` is not a proper timestamp.")
    
def check_for_numeric_cols(data, cols):
    """Make sure the column(s) is/are numeric.

    Parameters
    ----------
    data : pd.DataFrame
        Tabular data containing `cols`.
    cols : list
        A list of column names to check.
    """
    for col in cols:
        if not pd.core.dtypes.common.is_numeric_dtype(data[col]):
            raise TypeError(f"Column `{col}` is not numeric. Please convert to a numeric dtype before proceeding.")
