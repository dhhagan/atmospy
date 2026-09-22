"""Test the trend plots."""
import matplotlib as mpl
import numpy as np
import pytest

from atmospy import calendarplot, dielplot


def test_dielplot_basics(hourly):
    ax = dielplot(hourly, x="timestamp", y="pm25")

    assert isinstance(ax, mpl.axes.Axes)

    # 24 hourly points plus the wrapped-around first point
    line = ax.lines[0]
    assert line.get_xdata().size == 25

    expected = hourly.groupby(hourly["timestamp"].dt.hour)["pm25"].mean().to_numpy()
    np.testing.assert_allclose(line.get_ydata()[:24], expected)
    assert line.get_ydata()[24] == line.get_ydata()[0]

    # the IQR band is the only filled collection
    assert len(ax.collections) == 1


def test_dielplot_without_iqr(hourly):
    ax = dielplot(hourly, x="timestamp", y="pm25", show_iqr=False)

    assert len(ax.collections) == 0


def test_dielplot_labels_and_limits(hourly):
    ax = dielplot(
        hourly, x="timestamp", y="pm25",
        xlabel="Hour", ylabel="PM2.5", title="Diel", ylim=(0, 50),
    )

    assert ax.get_xlabel() == "Hour"
    assert ax.get_ylabel() == "PM2.5"
    assert ax.get_title() == "Diel"
    assert ax.get_ylim() == (0, 50)


def test_dielplot_requires_timestamp_column(hourly):
    with pytest.raises(TypeError):
        dielplot(hourly, x="pm25", y="ws")


def test_calendarplot_by_day(hourly):
    ax = calendarplot(hourly, x="timestamp", y="pm25", freq="day", vmin=0, vmax=50)

    assert isinstance(ax, mpl.axes.Axes)

    mesh = ax.collections[0]
    assert mesh.get_array().size == 7 * 52
    assert mesh.get_clim() == (0, 50)


def test_calendarplot_by_hour(hourly):
    january = hourly[hourly["timestamp"].dt.month == 1]
    ax = calendarplot(january, x="timestamp", y="pm25", freq="hour", title="Jan")

    mesh = ax.collections[0]
    assert mesh.get_array().size == 24 * 31
    assert ax.get_title() == "Jan"


def test_calendarplot_invalid_freq(hourly):
    with pytest.raises(ValueError):
        calendarplot(hourly, x="timestamp", y="pm25", freq="week")


def test_calendarplot_requires_timestamp_column(hourly):
    with pytest.raises(TypeError):
        calendarplot(hourly, x="pm25", y="ws")
