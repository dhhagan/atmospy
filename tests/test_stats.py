"""Test the statistical functions."""
import numpy as np
import pandas as pd
import pytest

from atmospy.stats import SensorStatsResults, air_sensor_stats, fleet_precision


def test_fleet_precision_requires_three_devices(sensors):
    with pytest.raises(ValueError):
        fleet_precision(sensors[["Sensor A", "Sensor B"]])


def test_fleet_precision_identical_devices_is_zero():
    x = np.linspace(1.0, 100.0, 50)
    stdev, cv = fleet_precision(pd.DataFrame({"a": x, "b": x, "c": x}))

    assert stdev == pytest.approx(0.0)
    assert cv == pytest.approx(0.0)


def test_fleet_precision_known_value():
    # Two records from three devices. Row means are 2 and 3, so every
    # deviation is -1, 0, or 1: the sum of squares is 4 and N*M - 1 is 5.
    df = pd.DataFrame({"a": [1.0, 2.0], "b": [2.0, 3.0], "c": [3.0, 4.0]})
    stdev, cv = fleet_precision(df)

    assert stdev == pytest.approx(np.sqrt(4.0 / 5.0))
    # EPA Eq. 4: CV is SD over the deployment-averaged concentration, in percent
    assert cv == pytest.approx(100.0 * np.sqrt(4.0 / 5.0) / 2.5)


def test_fleet_precision_drops_incomplete_records():
    df = pd.DataFrame({"a": [1.0, 2.0, np.nan], "b": [2.0, 3.0, 5.0], "c": [3.0, 4.0, 9.0]})
    assert fleet_precision(df) == pytest.approx(fleet_precision(df.iloc[:2]))


def test_fleet_precision_on_synthetic_fleet(sensors):
    stdev, cv = fleet_precision(sensors[["Sensor A", "Sensor B", "Sensor C"]])

    assert stdev > 0.0
    assert 0.0 < cv < 100.0


def test_air_sensor_stats_rejects_nan():
    with pytest.raises(ValueError):
        air_sensor_stats([1.0, np.nan], [1.0, 2.0])

    with pytest.raises(ValueError):
        air_sensor_stats([1.0, 2.0], [np.nan, 2.0])


def test_air_sensor_stats_exact_linear_relationship():
    actual = np.arange(1.0, 11.0)
    predicted = 2.0 * actual + 1.0

    res = air_sensor_stats(actual, predicted)

    assert isinstance(res, SensorStatsResults)
    assert res.slope == pytest.approx(2.0)
    assert res.intercept == pytest.approx(1.0)
    assert res.pearson_r2 == pytest.approx(1.0)
    assert res.mae == pytest.approx(np.mean(np.abs(predicted - actual)))
    assert res.rmse == pytest.approx(np.sqrt(np.mean((predicted - actual) ** 2)))
    assert res.nobs == 10


def test_air_sensor_stats_nrmse_is_normalized_by_reference_mean():
    # EPA Eq. 6: NRMSE = RMSE / mean(reference) * 100. With the sensor reading
    # exactly double the reference, the two candidate denominators differ by 2x,
    # so this pins the reference mean as the correct one.
    actual = np.array([2.0, 4.0, 6.0, 8.0])
    predicted = 2.0 * actual

    res = air_sensor_stats(actual, predicted)

    expected_rmse = np.sqrt(np.mean((predicted - actual) ** 2))
    assert res.rmse == pytest.approx(expected_rmse)
    assert res.nrmse == pytest.approx(100.0 * expected_rmse / actual.mean())
    assert res.nrmse != pytest.approx(100.0 * expected_rmse / predicted.mean())


def test_air_sensor_stats_asdict(sensors):
    res = air_sensor_stats(sensors["Reference"], sensors["Sensor A"])
    d = res.asdict()

    assert isinstance(d, dict)
    assert set(d) == {"slope", "intercept", "pearson_r2", "mae", "rmse", "nrmse", "nobs"}
    assert res.slope == pytest.approx(1.10, abs=0.05)
    assert res.pearson_r2 > 0.9
