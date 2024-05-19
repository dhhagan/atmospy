"""Utility functions for internal use."""

import numpy as np
import pandas as pd
from scipy.stats import linregress
from dataclasses import dataclass, asdict

__all__ = [
    "fleet_precision", 
    "air_sensor_stats", 
]

@dataclass
class SensorStatsResults:
    """"""
    slope: float
    intercept: float
    pearson_r2: float
    mae: float
    rmse: float
    nrmse: float
    nobs: int
    
    asdict = asdict

def _error(actual: np.ndarray, predicted: np.ndarray):
    return actual - predicted

def mae(actual: np.ndarray, predicted: np.ndarray):
    return np.mean(np.abs(_error(actual, predicted)))

def mse(actual: np.ndarray, predicted: np.ndarray):
    return np.mean(np.square(_error(actual, predicted)))

def rmse(actual: np.ndarray, predicted: np.ndarray):
    return np.sqrt(mse(actual, predicted))

def nrmse(actual: np.ndarray, predicted: np.ndarray):
    return rmse(actual, predicted) / np.mean(actual)

def fleet_precision(data: pd.DataFrame):
    """Compute the precision across a fleet of at least three (3) devices.
    
    The math used here comes from the `EPA's Air Sensor Performance Targets 
    and Testing Protocols guidelines <https://www.epa.gov/air-sensor-toolbox/air-sensor-performance-targets-and-testing-protocols>`_.

    Parameters
    ----------
    data : pd.DataFrame
        A dataframe containing a wide-form dataframe as a time series where the 
        index is a timestamp. Each column should represent the same pollutant 
        or other measure for a unique device, whether it is an air sensor 
        or other instrument.

    Returns
    -------
    stdev, cv : tuple(float, float)
        Returns the standard deviation and coeficient of variation.
    """
    # drop any record with a NaN present
    data = data.dropna(how='any')
    
    # ensure there are at least 3 devices
    if data.shape[1] < 3:
        raise ValueError(f"You must have at least three columns; you provided {data.shape[1]}.")
    
    # compute the standard deviation
    sum_of_squares = (
        data.sub(data.mean(axis=1).values, axis=0)**2
    ).values.sum()
    
    stdev = np.sqrt(
        ((1 / (data.shape[0]*data.shape[1] - 1))) * sum_of_squares
    )
    
    # compute the coefficient of variation
    cv = stdev / data.values.mean()
    
    return stdev, cv

def air_sensor_stats(actual: np.ndarray, predicted: np.ndarray):
    """Compute the statistical measures required by EPA for 
    Air Sensor NSIM evaluation per their guidebooks.

    Parameters
    ----------
    actual : np.ndarray
        An array of numeric types with the reference values (i.e., y_true in sklearn language).
    predicted : np.ndarray
        An array of numeric types with the air sensor values (i.e., y_pred in sklearn language).
        
    Returns
    -------
    results: SensorStatsResults
        An instance of the SensorStatsResults dataclass with 
        fit data results including slope, intercept, MAE, RMSE,
        NRMSE, NOBS, and Pearson-R2.
    
    """
    # force to arrays
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)
    
    if np.isnan(actual).any():
        raise ValueError("You cannot have NaN's present in your `actual` array.")
    
    if np.isnan(predicted).any():
        raise ValueError("You cannot have NaN's present in your `predicted` array.")
    
    # fit the data to a linear model
    fit = linregress(predicted, actual)
    
    return SensorStatsResults(
        fit.slope,
        fit.intercept,
        fit.rvalue**2,
        mae(predicted, actual),
        rmse(predicted, actual),
        nrmse(predicted, actual),
        actual.shape[0]
    )