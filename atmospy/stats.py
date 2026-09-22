"""Statistical measures for evaluating air sensor performance.

The formulas follow the U.S. EPA *Performance Testing Protocols, Metrics, and
Target Values* reports for air sensors used in non-regulatory supplemental and
informational monitoring (NSIM), e.g. EPA/600/R-20/280 for PM2.5. Equation
numbers referenced below are from that report.
"""

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
    """Bias, linearity, and error statistics for one sensor against a reference.

    Attributes
    ----------
    slope : float
        Slope of the ordinary least squares regression of the sensor (y)
        on the reference (x).
    intercept : float
        Intercept of that regression, in measurement units.
    pearson_r2 : float
        Coefficient of determination (R²) of that regression.
    mae : float
        Mean absolute error between sensor and reference, in measurement units.
    rmse : float
        Root mean square error between sensor and reference (EPA Eq. 5),
        in measurement units.
    nrmse : float
        RMSE normalized by the mean reference concentration (EPA Eq. 6),
        in percent.
    nobs : int
        Number of paired observations used.
    """
    slope: float
    intercept: float
    pearson_r2: float
    mae: float
    rmse: float
    nrmse: float
    nobs: int

    def asdict(self):
        """Return the results as a plain dictionary."""
        return asdict(self)


def _error(actual: np.ndarray, predicted: np.ndarray):
    return actual - predicted


def mae(actual: np.ndarray, predicted: np.ndarray):
    """Mean absolute error, in measurement units."""
    return np.mean(np.abs(_error(actual, predicted)))


def mse(actual: np.ndarray, predicted: np.ndarray):
    """Mean squared error, in squared measurement units."""
    return np.mean(np.square(_error(actual, predicted)))


def rmse(actual: np.ndarray, predicted: np.ndarray):
    """Root mean square error (EPA Eq. 5), in measurement units."""
    return np.sqrt(mse(actual, predicted))


def nrmse(actual: np.ndarray, predicted: np.ndarray):
    """RMSE normalized by the mean of ``actual`` (EPA Eq. 6), in percent."""
    return 100.0 * rmse(actual, predicted) / np.mean(actual)


def fleet_precision(data: pd.DataFrame):
    """Compute the precision across a fleet of at least three (3) devices.

    Precision is reported as the standard deviation (SD, EPA Eq. 3) and the
    coefficient of variation (CV, EPA Eq. 4) across identical sensors that
    are collocated and reporting concurrently. The math comes from the
    `EPA's Air Sensor Performance Targets and Testing Protocols guidelines
    <https://www.epa.gov/air-sensor-toolbox/air-sensor-performance-targets-and-testing-protocols>`_.

    EPA computes these metrics on 24-hour averages. This function uses
    whatever cadence you pass in, so resample first if you want to follow
    the protocol exactly.

    Parameters
    ----------
    data : pd.DataFrame
        A wide-form time series where the index is a timestamp and each
        column holds the same measurement from a different device. Any
        record with a missing value in any column is dropped, so only
        periods where every device reported are used.

    Returns
    -------
    stdev, cv : tuple(float, float)
        The standard deviation in measurement units and the coefficient
        of variation in percent.

    Examples
    --------
    >>> stdev, cv = atmospy.fleet_precision(df[["Sensor A", "Sensor B", "Sensor C"]])
    """
    # drop any record with a NaN present
    data = data.dropna(how='any')

    # ensure there are at least 3 devices
    if data.shape[1] < 3:
        raise ValueError(f"You must have at least three columns; you provided {data.shape[1]}.")

    # EPA Eq. 3: deviations of each device from the fleet mean at each timestamp
    sum_of_squares = (
        data.sub(data.mean(axis=1).values, axis=0)**2
    ).values.sum()

    stdev = np.sqrt(
        ((1 / (data.shape[0]*data.shape[1] - 1))) * sum_of_squares
    )

    # EPA Eq. 4: normalized by the deployment-averaged sensor concentration, in percent
    cv = 100.0 * stdev / data.values.mean()

    return stdev, cv


def air_sensor_stats(actual: np.ndarray, predicted: np.ndarray):
    """Compute the EPA bias, linearity, and error metrics for one air sensor.

    The sensor is regressed on the reference (sensor as y, reference as x)
    to obtain the slope, intercept, and R² used for the EPA bias and
    linearity targets, and the error metrics of EPA Eq. 5 and Eq. 6 are
    computed from the paired values.

    EPA computes these metrics on 24-hour averages. This function uses
    whatever cadence you pass in, so resample first if you want to follow
    the protocol exactly.

    Parameters
    ----------
    actual : np.ndarray
        The reference (FRM/FEM) values, i.e. y_true in sklearn language.
    predicted : np.ndarray
        The air sensor values, i.e. y_pred in sklearn language.

    Returns
    -------
    results : SensorStatsResults
        Slope, intercept, R², MAE, RMSE, NRMSE (in percent), and the
        number of observations.

    Examples
    --------
    >>> res = atmospy.air_sensor_stats(df["Reference"], df["Sensor A"])
    >>> res.nrmse
    """
    # force to arrays
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)

    if np.isnan(actual).any():
        raise ValueError("You cannot have NaN's present in your `actual` array.")

    if np.isnan(predicted).any():
        raise ValueError("You cannot have NaN's present in your `predicted` array.")

    # fit the sensor (y) against the reference (x)
    fit = linregress(actual, predicted)

    return SensorStatsResults(
        fit.slope,
        fit.intercept,
        fit.rvalue**2,
        mae(actual, predicted),
        rmse(actual, predicted),
        nrmse(actual, predicted),
        actual.shape[0]
    )
