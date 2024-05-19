"""Test the statistical functions."""

import pytest
import numpy as np
from atmospy.stats import *
from atmospy import load_dataset

def test_fleet_precision():
    df = load_dataset("air-sensors-pm")
    
    # a ValueError should be raised if fewer than 3 columns are present
    with pytest.raises(ValueError):
        fleet_precision(df[["Sensor A", "Sensor B"]])
    
    stdev, cv = fleet_precision(df[["Sensor A", "Sensor B", "Sensor C"]])
    
    assert cv <= 1.0

def test_sensor_stats():
    df = load_dataset("air-sensors-pm")

    # Compute the linear fit for a single device
    with pytest.raises(ValueError):
        fit = air_sensor_stats(df["Reference"], df["Sensor A"])
        
    df = df[["Reference", "Sensor A"]].dropna()
    
    stats = air_sensor_stats(df["Reference"], df["Sensor A"])

    assert ~np.isnan(stats.slope)
    assert ~np.isnan(stats.intercept)
    assert ~np.isnan(stats.pearson_r2)
    assert ~np.isnan(stats.mae)
    assert ~np.isnan(stats.rmse)
    assert ~np.isnan(stats.nrmse)
    assert ~np.isnan(stats.nobs)
    
    assert isinstance(stats.asdict(), dict)
    
    