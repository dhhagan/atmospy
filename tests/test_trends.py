"""Test the trend plots."""
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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


def test_dielplot_iqr_band_matches_quantiles(hourly):
    ax = dielplot(hourly, x="timestamp", y="pm25")

    by_hour = hourly.groupby(hourly["timestamp"].dt.hour)["pm25"]
    band = ax.collections[0]
    # fill_between stores the polygon as (x, y1) then (x, y2) reversed
    verts = band.get_paths()[0].vertices
    n = 25
    lower = verts[1:n + 1, 1]
    upper = verts[n + 2:2 * n + 2, 1][::-1]
    np.testing.assert_allclose(lower[:24], by_hour.quantile(0.25).to_numpy())
    np.testing.assert_allclose(upper[:24], by_hour.quantile(0.75).to_numpy())


def test_dielplot_without_iqr(hourly):
    ax = dielplot(hourly, x="timestamp", y="pm25", show_iqr=False)

    assert len(ax.collections) == 0


def test_dielplot_handles_irregular_sampling(hourly, rng):
    # drop a third of the rows and jitter the rest by up to 20 minutes so no
    # two days share the same (hour, minute) pattern
    keep = rng.random(len(hourly)) > 0.33
    irregular = hourly[keep].copy()
    irregular["timestamp"] += pd.to_timedelta(rng.integers(0, 20 * 60, size=len(irregular)), unit="s")

    ax = dielplot(irregular, x="timestamp", y="pm25")

    line = ax.lines[0]
    assert line.get_xdata().size == 25

    expected = irregular.groupby(irregular["timestamp"].dt.hour)["pm25"].mean().to_numpy()
    np.testing.assert_allclose(line.get_ydata()[:24], expected)


def test_dielplot_custom_freq(hourly):
    ax = dielplot(hourly, x="timestamp", y="pm25", freq="6h")

    line = ax.lines[0]
    assert line.get_xdata().size == 5

    expected = hourly.groupby(hourly["timestamp"].dt.hour // 6)["pm25"].mean().to_numpy()
    np.testing.assert_allclose(line.get_ydata()[:4], expected)


def test_dielplot_leaves_gaps_for_empty_bins(hourly):
    daytime = hourly[hourly["timestamp"].dt.hour.between(8, 17)]

    ax = dielplot(daytime, x="timestamp", y="pm25")

    ydata = ax.lines[0].get_ydata()
    assert np.isnan(ydata[:8]).all()
    assert np.isfinite(ydata[8:18]).all()
    assert np.isnan(ydata[18:24]).all()


@pytest.mark.parametrize("freq", ["7h", "50min", "MS", "1D", "36h", "0h", "not-a-freq"])
def test_dielplot_rejects_bad_freq(hourly, freq):
    with pytest.raises(ValueError):
        dielplot(hourly, x="timestamp", y="pm25", freq=freq)


def test_dielplot_applies_default_linewidth(hourly):
    ax = dielplot(hourly, x="timestamp", y="pm25")

    assert ax.lines[0].get_linewidth() == 3


def test_dielplot_merges_plot_kws_and_color(hourly):
    ax = dielplot(hourly, x="timestamp", y="pm25", color="g", plot_kws={"ls": "--"})

    line = ax.lines[0]
    assert line.get_linewidth() == 3
    assert line.get_linestyle() == "--"
    assert line.get_color() == "g"


def test_dielplot_uses_given_axes_for_band_color(hourly):
    _, (ax1, ax2) = plt.subplots(1, 2)
    ax2.plot([0, 1], [0, 1], color="red")
    plt.sca(ax2)

    ax = dielplot(hourly, x="timestamp", y="pm25", ax=ax1, color="blue")

    assert ax is ax1
    band_color = ax1.collections[0].get_facecolor()[0][:3]
    np.testing.assert_allclose(band_color, mpl.colors.to_rgb("blue"))
    assert len(ax2.collections) == 0


def test_dielplot_tz_aware_timestamps(hourly):
    # a fixed-offset zone (UTC-7) so no DST gap makes a local time nonexistent
    aware = hourly.assign(timestamp=hourly["timestamp"].dt.tz_localize("Etc/GMT+7"))

    ax = dielplot(aware, x="timestamp", y="pm25")

    expected = hourly.groupby(hourly["timestamp"].dt.hour)["pm25"].mean().to_numpy()
    np.testing.assert_allclose(ax.lines[0].get_ydata()[:24], expected)


def test_dielplot_axis_spans_one_day(hourly):
    ax = dielplot(hourly, x="timestamp", y="pm25")

    lo, hi = mpl.dates.num2date(ax.get_xlim())
    assert (hi - lo).total_seconds() == 24 * 3600
    labels = [t.get_text() for t in ax.get_xticklabels()]
    assert labels == ["12:00\nAM", "06:00\nAM", "12:00\nPM", "06:00\nPM", "12:00\nAM"]


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
