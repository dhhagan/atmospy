"""Test the trend plots."""
import warnings

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


def _year_frame(year, value=1.0):
    t = pd.date_range(f"{year}-01-01", f"{year}-12-31 23:00", freq="h")
    return pd.DataFrame({"timestamp": t, "pm25": value})


def test_calendarplot_by_day(hourly):
    ax = calendarplot(hourly, x="timestamp", y="pm25", freq="day", vmin=0, vmax=50)

    assert isinstance(ax, mpl.axes.Axes)

    mesh = ax.collections[0]
    # 2023 starts on a Sunday, so the grid needs 53 Monday-based week columns
    assert mesh.get_array().size == 7 * 53
    assert mesh.get_clim() == (0, 50)


@pytest.mark.parametrize("year, n_days", [(2020, 366), (2023, 365), (2024, 366), (2021, 365)])
def test_calendarplot_by_day_keeps_every_day(year, n_days):
    # 2020 ends in ISO week 53; 2023 starts on a Sunday that ISO assigns to 2022;
    # 2024 starts on a Monday; 2021 starts on a Friday.
    ax = calendarplot(_year_frame(year), x="timestamp", y="pm25", freq="day")

    mesh = ax.collections[0]
    assert np.ma.count(mesh.get_array()) == n_days


def test_calendarplot_by_day_places_days_by_weekday():
    # Jan 1 2023 is a Sunday: it must be alone in the first column, bottom row
    ax = calendarplot(_year_frame(2023), x="timestamp", y="pm25", freq="day")

    grid = np.ma.getmaskarray(ax.collections[0].get_array()).reshape(7, -1)
    first_column_present = ~grid[:, 0]
    assert first_column_present.tolist() == [True, False, False, False, False, False, False]
    assert ax.get_ylabel() == "2023"


def test_calendarplot_by_day_month_labels_align_with_months():
    ax = calendarplot(_year_frame(2023), x="timestamp", y="pm25", freq="day")

    labels = [t.get_text() for t in ax.get_xticklabels()]
    assert labels == ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    centers = ax.xaxis.get_majorticklocs()
    assert np.all(np.diff(centers) > 0)
    # The grid starts on Mon Dec 26 2022. Jan runs from Sun Jan 1 (day 6) to
    # Feb 1 (day 37), so its label sits at the midpoint of those in week units.
    assert centers[0] == pytest.approx((6 / 7 + 37 / 7) / 2)

    boundaries = ax.xaxis.get_minorticklocs()
    assert len(boundaries) == 13
    assert boundaries[0] == pytest.approx(6 / 7)  # Sun Jan 1 is 6 days after Mon Dec 26


@pytest.mark.parametrize("freq", ["day", "hour"])
def test_calendarplot_single_period_emits_no_warnings(freq):
    df = _year_frame(2023)
    if freq == "hour":
        df = df[df["timestamp"].dt.month == 3]

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        calendarplot(df, x="timestamp", y="pm25", freq=freq)


def test_calendarplot_by_day_warns_on_multiple_years():
    df = pd.concat([_year_frame(2022), _year_frame(2023), _year_frame(2024)])

    with pytest.warns(UserWarning, match=r"plotting 2022 and ignoring 2023, 2024"):
        ax = calendarplot(df, x="timestamp", y="pm25", freq="day")

    assert ax.get_ylabel() == "2022"


def test_calendarplot_by_hour_warns_on_multiple_months():
    df = _year_frame(2023)
    df = df[df["timestamp"].dt.month.isin([3, 4])]

    with pytest.warns(UserWarning, match=r"plotting 2023-03 and ignoring 2023-04"):
        ax = calendarplot(df, x="timestamp", y="pm25", freq="hour")

    assert ax.collections[0].get_array().size == 24 * 31


def test_calendarplot_by_hour_distinguishes_same_month_in_different_years():
    df = pd.concat([_year_frame(2022), _year_frame(2023)])
    df = df[df["timestamp"].dt.month == 1]

    with pytest.warns(UserWarning, match=r"plotting 2022-01 and ignoring 2023-01"):
        ax = calendarplot(df, x="timestamp", y="pm25", freq="hour")

    assert np.ma.count(ax.collections[0].get_array()) == 24 * 31


@pytest.mark.parametrize("freq", ["day", "hour"])
def test_calendarplot_draws_on_given_axes(freq):
    df = _year_frame(2023)
    if freq == "hour":
        df = df[df["timestamp"].dt.month == 3]

    _, (ax1, ax2) = plt.subplots(2, 1)
    plt.sca(ax2)

    ax = calendarplot(df, x="timestamp", y="pm25", freq=freq, ax=ax1, cbar=False)

    assert ax is ax1
    assert len(ax1.collections) == 1
    assert len(ax2.collections) == 0


def test_calendarplot_by_day_tz_aware():
    df = _year_frame(2023)
    df["timestamp"] = df["timestamp"].dt.tz_localize("Etc/GMT+5")

    ax = calendarplot(df, x="timestamp", y="pm25", freq="day")

    assert np.ma.count(ax.collections[0].get_array()) == 365


def test_calendarplot_by_hour(hourly):
    january = hourly[hourly["timestamp"].dt.month == 1]
    ax = calendarplot(january, x="timestamp", y="pm25", freq="hour", title="Jan")

    mesh = ax.collections[0]
    assert mesh.get_array().size == 24 * 31
    assert ax.get_title() == "Jan"


def _colorbar_axes(ax):
    others = [a for a in ax.figure.axes if a is not ax]
    assert len(others) == 1, "expected exactly one colorbar axes"
    return others[0]


@pytest.mark.parametrize("freq", ["day", "hour"])
def test_calendarplot_colorbar_is_labeled_with_units(hourly, freq):
    january = hourly[hourly["timestamp"].dt.month == 1]
    ax = calendarplot(january, x="timestamp", y="pm25", freq=freq, units="ppb")

    cb_ax = _colorbar_axes(ax)
    assert cb_ax.get_ylabel() == "ppb"

    # the locator may propose ticks beyond the colorbar's range that are never drawn
    lo, hi = sorted(cb_ax.get_ylim())
    ticks = cb_ax.get_yticks()
    visible = ticks[(ticks >= lo) & (ticks <= hi)]
    assert 2 <= len(visible) <= 5


@pytest.mark.parametrize("freq", ["day", "hour"])
def test_calendarplot_colorbar_without_units_has_no_label(hourly, freq):
    january = hourly[hourly["timestamp"].dt.month == 1]
    ax = calendarplot(january, x="timestamp", y="pm25", freq=freq)

    assert _colorbar_axes(ax).get_ylabel() == ""


def test_calendarplot_horizontal_colorbar_labels_x_axis(hourly):
    ax = calendarplot(
        hourly, x="timestamp", y="pm25", freq="day", units="ppb",
        cbar_kws={"orientation": "horizontal"},
    )

    cb_ax = _colorbar_axes(ax)
    assert cb_ax.get_xlabel() == "ppb"
    assert cb_ax.get_ylabel() == ""


@pytest.mark.parametrize("freq", ["day", "hour"])
def test_calendarplot_colorbar_caps_when_vmax_clips(hourly, freq):
    january = hourly[hourly["timestamp"].dt.month == 1]

    ax = calendarplot(january, x="timestamp", y="pm25", freq=freq)
    assert _colorbar_axes(ax)._colorbar.extend == "neither"

    plt.figure()
    ax = calendarplot(january, x="timestamp", y="pm25", freq=freq, vmax=10)
    assert _colorbar_axes(ax)._colorbar.extend == "max"


@pytest.mark.parametrize("freq", ["day", "hour"])
def test_calendarplot_does_not_mutate_cbar_kws(hourly, freq):
    january = hourly[hourly["timestamp"].dt.month == 1]
    kws = {"shrink": 0.5}

    calendarplot(january, x="timestamp", y="pm25", freq=freq, cbar_kws=kws)

    assert kws == {"shrink": 0.5}


@pytest.mark.parametrize("freq", ["day", "hour"])
def test_calendarplot_without_colorbar(hourly, freq):
    january = hourly[hourly["timestamp"].dt.month == 1]
    ax = calendarplot(january, x="timestamp", y="pm25", freq=freq, cbar=False)

    assert ax.figure.axes == [ax]


def test_calendarplot_invalid_freq(hourly):
    with pytest.raises(ValueError):
        calendarplot(hourly, x="timestamp", y="pm25", freq="week")


def test_calendarplot_requires_timestamp_column(hourly):
    with pytest.raises(TypeError):
        calendarplot(hourly, x="pm25", y="ws")
