"""Test the pollution rose plots."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import seaborn as sns

from atmospy import pollutionroseplot

COMPASS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def _bar_total(ax):
    return sum(sum(bar.get_height() for bar in c) for c in ax.containers)


def _legend_labels(ax):
    return [t.get_text() for t in ax.get_legend().get_texts()]


# --- stacked ---------------------------------------------------------------

def test_stacked_basics(hourly):
    calm = 0.5
    ax = pollutionroseplot(
        data=hourly, ws="ws", wd="wd", pollutant="pm25",
        bins=[0, 10, 20, 40], segments=12, calm=calm,
    )

    assert ax.name == "polar"

    # three closed bins plus the open-ended catch-all, one stacked bar per sector
    assert len(ax.containers) == 4
    assert all(len(container) == 12 for container in ax.containers)

    # the stacked bars account for exactly the non-calm fraction of the data
    assert _bar_total(ax) == pytest.approx(100.0 * (hourly["ws"] > calm).mean())


def test_stacked_labels_and_compass(hourly):
    ax = pollutionroseplot(
        data=hourly, ws="ws", wd="wd", pollutant="pm25",
        bins=[0, 10, 20], suffix="ppb", title="rose",
    )

    assert _legend_labels(ax) == ["0 to 10 ppb", "10 to 20 ppb", "≥20 ppb"]
    assert ax.get_title() == "rose"
    assert [t.get_text() for t in ax.get_xticklabels()] == COMPASS


def test_stacked_without_legend(hourly):
    ax = pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", bins=[0, 10], legend=False)

    assert ax.get_legend() is None


def test_stacked_counts_records_on_bin_edges():
    # wind from exactly 0° and 360°, and a pollutant reading of exactly 0,
    # must all be counted rather than falling outside right-closed bins
    df = pd.DataFrame({"ws": [3.0] * 4, "wd": [0.0, 360.0, 90.0, 180.0], "pm25": [5.0, 5.0, 0.0, 5.0]})

    ax = pollutionroseplot(data=df, ws="ws", wd="wd", pollutant="pm25", bins=[0, 10], calm=0)

    assert _bar_total(ax) == pytest.approx(100.0)


def test_stacked_sectors_are_centered_on_north():
    # 350° and 10° both belong to the north sector; 20° does not (12 sectors of 30°)
    df = pd.DataFrame({"ws": [3.0] * 3, "wd": [350.0, 10.0, 20.0], "pm25": [1.0] * 3})

    ax = pollutionroseplot(data=df, ws="ws", wd="wd", pollutant="pm25", bins=[0, 10], calm=0)

    heights = [bar.get_height() for bar in ax.containers[0]]
    north, northeast_ish = heights[0], heights[1]
    assert north == pytest.approx(200.0 / 3)
    assert northeast_ish == pytest.approx(100.0 / 3)
    assert ax.containers[0][0].get_x() == pytest.approx(np.radians(-15.0))


def test_stacked_calm_hole_matches_calm_share():
    df = pd.DataFrame({"ws": [0.0, 0.0, 5.0, 5.0], "wd": [0.0] * 4, "pm25": [1.0] * 4})

    ax = pollutionroseplot(data=df, ws="ws", wd="wd", pollutant="pm25", bins=[0, 10], segments=4, calm=0.1)

    # bars start at the edge of the hole, and the hole is half the radius
    # because half the records are calm
    assert ax.containers[0][0].get_y() == 0
    assert _bar_total(ax) == pytest.approx(50.0)

    origin, top = ax.get_rorigin(), ax.get_ylim()[1]
    assert -origin / (top - origin) == pytest.approx(0.5)


def test_stacked_no_calm_means_no_hole(hourly):
    ax = pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", bins=[0, 10], calm=-1)

    assert ax.get_rorigin() == 0


def test_stacked_percent_rings(hourly):
    ax = pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", bins=[0, 10, 20], segments=12)

    tallest = max(sum(c[i].get_height() for c in ax.containers) for i in range(12))
    ticks = ax.yaxis.get_majorticklocs()
    labels = [t.get_text() for t in ax.get_yticklabels()]

    assert 1 <= len(ticks) <= 3
    assert all(0 < t <= tallest for t in ticks)
    assert labels == [f"{t:g}%" for t in ticks]
    assert ax.get_ylim()[1] == pytest.approx(tallest * 1.05)


def test_bins_are_not_mutated(hourly):
    bins = [0, 10, 100]
    pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", bins=bins)

    assert bins == [0, 10, 100]


def test_bins_accept_numpy_arrays_and_tuples(hourly):
    ax = pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", bins=np.array([0, 10, 100]))
    assert len(ax.containers) == 3

    plt.figure()
    ax = pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", bins=(0, 10, 100, np.inf))
    assert len(ax.containers) == 3


@pytest.mark.parametrize("bins", [[5], [0, 10, 10], [10, 0]])
def test_invalid_bins_raise(hourly, bins):
    with pytest.raises(ValueError, match="bins"):
        pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", bins=bins)


# --- heatmap ---------------------------------------------------------------

def test_heatmap_cells_match_groupby_mean(hourly):
    ws_bins = [0, 2, 4, 8]
    ax = pollutionroseplot(
        data=hourly, ws="ws", wd="wd", pollutant="pm25",
        kind="heatmap", segments=8, ws_bins=ws_bins, calm=0, cbar=False,
    )

    mesh = ax.collections[0]
    grid = np.ma.filled(mesh.get_array().reshape(3, 8), np.nan)

    # recompute by hand: sectors centered on north, speeds clipped into the outer ring
    sector = np.floor(((hourly["wd"] + 22.5) % 360) / 45).astype(int)
    ring = np.clip(np.searchsorted(ws_bins, hourly["ws"], side="right") - 1, 0, 2)
    expected = (
        hourly.assign(sector=sector, ring=ring)
        .groupby(["ring", "sector"])["pm25"].mean()
        .unstack("sector").reindex(index=range(3), columns=range(8))
        .to_numpy()
    )
    np.testing.assert_allclose(grid, expected)


def test_heatmap_cells_have_curved_arcs(hourly):
    ax = pollutionroseplot(
        data=hourly, ws="ws", wd="wd", pollutant="pm25",
        kind="heatmap", segments=8, ws_bins=[0, 2, 4, 8], cbar=False,
    )

    cells = ax.collections[0]
    paths = cells.get_paths()

    # one cell per ring x sector, ring-major so the array reshapes to the grid
    assert len(paths) == 3 * 8
    assert cells.get_array().shape == (24,)

    # arc interpolation is what keeps the edges round on polar axes
    assert all(path._interpolation_steps > 1 for path in paths)

    # empty cells draw no edge, filled cells draw a white one
    masked = np.ma.getmaskarray(cells.get_array())
    edges = cells.get_edgecolors()
    assert len(edges) == 24
    for is_masked, edge in zip(masked, edges):
        assert edge[3] == (0.0 if is_masked else 1.0)


def test_heatmap_min_count_blanks_sparse_cells():
    df = pd.DataFrame({
        "ws": [1.0, 1.0, 1.0, 5.0],
        "wd": [0.0, 0.0, 0.0, 180.0],
        "pm25": [10.0, 20.0, 30.0, 99.0],
    })

    ax = pollutionroseplot(
        data=df, ws="ws", wd="wd", pollutant="pm25",
        kind="heatmap", segments=4, ws_bins=[0, 2, 6], calm=0, min_count=2, cbar=False,
    )

    grid = ax.collections[0].get_array().reshape(2, 4)
    assert grid[0, 0] == pytest.approx(20.0)      # three records from the north at low speed
    assert np.ma.is_masked(grid[1, 2])            # the lone southerly record is blanked
    assert np.ma.count(grid) == 1


def _heatmap_grid(df, **kwargs):
    ax = pollutionroseplot(data=df, ws="ws", wd="wd", pollutant="pm25", kind="heatmap", cbar=False, **kwargs)
    return np.ma.filled(ax.collections[0].get_array(), np.nan)


@pytest.mark.parametrize("agg, reducer", [
    ("mean", np.mean),
    ("median", np.median),
    ("min", np.min),
    ("max", np.max),
    ("p95", lambda v: np.percentile(v, 95)),
    ("p50", np.median),
    ("p2.5", lambda v: np.percentile(v, 2.5)),
    (lambda s: s.max() - s.min(), np.ptp),
])
def test_heatmap_agg_options(agg, reducer):
    # one sector, one ring, so the single cell is the reduction of all values
    values = np.array([1.0, 2.0, 4.0, 8.0, 16.0, 32.0])
    df = pd.DataFrame({"ws": [1.0] * 6, "wd": [0.0] * 6, "pm25": values})

    grid = _heatmap_grid(df, agg=agg, segments=1, ws_bins=[0, 2], calm=0)

    assert grid.size == 1
    assert grid.item() == pytest.approx(reducer(values))


def test_heatmap_agg_count():
    df = pd.DataFrame({"ws": [1.0] * 6, "wd": [0.0] * 6, "pm25": np.arange(6.0)})

    grid = _heatmap_grid(df, agg="count", segments=1, ws_bins=[0, 2], calm=0)

    assert grid.item() == 6


@pytest.mark.parametrize("agg", ["average", "p101", "p-5", "95th", 95, None])
def test_heatmap_rejects_unknown_agg(hourly, agg):
    with pytest.raises(ValueError, match="agg"):
        pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", kind="heatmap", agg=agg)


def test_heatmap_agg_and_color_limits(hourly):
    ax = pollutionroseplot(
        data=hourly, ws="ws", wd="wd", pollutant="pm25",
        kind="heatmap", agg="max", vmin=0, vmax=50, cbar=False,
    )

    mesh = ax.collections[0]
    assert mesh.get_clim() == (0, 50)
    assert np.nanmax(np.ma.filled(mesh.get_array(), np.nan)) == pytest.approx(hourly["pm25"].max())


def test_heatmap_default_rings_and_labels(hourly):
    ax = pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", kind="heatmap", calm=0.5, cbar=False)

    # fifteen 1 m/s rings from 0 to 15, with gridlines and labels only every 5
    assert ax.collections[0].get_array().size == 15 * 12
    np.testing.assert_allclose(ax.yaxis.get_majorticklocs(), [5, 10, 15])
    assert [t.get_text() for t in ax.get_yticklabels()] == ["5", "10", "≥15"]
    assert ax.get_ylim() == (0, 15)


@pytest.mark.parametrize("ws_bins, positions, labels", [
    ([0, 2, 4, 6], [2, 4, 6], ["2", "4", "≥6"]),                 # three rings: every edge
    (list(range(9)), [4, 8], ["4", "≥8"]),                       # eight rings: every 4th, outer always kept
    ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [5, 10], ["5", "≥10"]),  # ten rings: every 5th
    ([0, 0.5, 1.0, 1.5, 2.0], [1, 2], ["1", "≥2"]),               # four rings: every 2nd
])
def test_heatmap_major_rings_are_data_driven(ws_bins, positions, labels):
    df = pd.DataFrame({"ws": [1.0, 3.0, 5.0], "wd": [0.0, 90.0, 180.0], "pm25": [1.0, 2.0, 3.0]})

    ax = pollutionroseplot(
        data=df, ws="ws", wd="wd", pollutant="pm25",
        kind="heatmap", ws_bins=ws_bins, calm=0, cbar=False,
    )

    np.testing.assert_allclose(ax.yaxis.get_majorticklocs(), positions)
    assert [t.get_text() for t in ax.get_yticklabels()] == labels
    assert len(labels) <= 3


def test_heatmap_speeds_above_outer_edge_fold_into_outer_ring():
    df = pd.DataFrame({"ws": [14.5, 40.0], "wd": [0.0, 0.0], "pm25": [10.0, 30.0]})

    ax = pollutionroseplot(data=df, ws="ws", wd="wd", pollutant="pm25", kind="heatmap", segments=4, calm=0, cbar=False)

    grid = ax.collections[0].get_array().reshape(15, 4)
    assert grid[14, 0] == pytest.approx(20.0)
    assert np.ma.count(grid) == 1


@pytest.mark.parametrize("vmin, vmax, extend", [
    (None, None, "neither"),
    (None, 20, "max"),
    (10, None, "min"),
    (10, 20, "both"),
])
def test_heatmap_colorbar_caps_when_values_are_clipped(hourly, vmin, vmax, extend):
    ax = pollutionroseplot(
        data=hourly, ws="ws", wd="wd", pollutant="pm25", kind="heatmap", vmin=vmin, vmax=vmax,
    )

    cb_ax = [a for a in ax.figure.axes if a is not ax][0]
    assert cb_ax._colorbar.extend == extend


def test_heatmap_colorbar_extend_can_be_overridden(hourly):
    ax = pollutionroseplot(
        data=hourly, ws="ws", wd="wd", pollutant="pm25", kind="heatmap",
        vmax=20, cbar_kws={"extend": "neither"},
    )

    cb_ax = [a for a in ax.figure.axes if a is not ax][0]
    assert cb_ax._colorbar.extend == "neither"
    assert [t.get_text() for t in ax.get_xticklabels()] == COMPASS


def test_heatmap_defaults_to_viridis(hourly):
    ax = pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", kind="heatmap", cbar=False)

    assert ax.collections[0].get_cmap().name == "viridis"


def _named_range(s):
    return s.max() - s.min()


@pytest.mark.parametrize("agg, suffix, label", [
    ("mean", "µg/m³", "mean (µg/m³)"),
    ("median", "ppb", "median (ppb)"),
    ("max", "ppb", "max (ppb)"),
    ("std", "ppb", "std. dev. (ppb)"),
    ("p95", "ppb", "95th percentile (ppb)"),
    ("p91", "ppb", "91st percentile (ppb)"),
    ("p2.5", "ppb", "2.5th percentile (ppb)"),
    ("count", "ppb", "count"),
    ("mean", "", "mean"),
    (_named_range, "ppb", "_named_range (ppb)"),
    (lambda s: s.max(), "ppb", "ppb"),
])
def test_heatmap_colorbar_label_folds_in_statistic(hourly, agg, suffix, label):
    ax = pollutionroseplot(
        data=hourly, ws="ws", wd="wd", pollutant="pm25", kind="heatmap", agg=agg, suffix=suffix,
    )

    others = [a for a in ax.figure.axes if a is not ax]
    assert len(others) == 1
    assert others[0].get_ylabel() == label


def test_heatmap_without_colorbar(hourly):
    ax = pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", kind="heatmap", cbar=False)

    assert ax.figure.axes == [ax]


# --- shared ----------------------------------------------------------------

@pytest.mark.parametrize("kind", ["stacked", "heatmap"])
def test_compass_tick_marks_point_outward(hourly, kind):
    ax = pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", kind=kind, cbar=False)
    ax.figure.canvas.draw()

    ticks = ax.xaxis.get_major_ticks()
    assert len(ticks) == 8

    for tick in ticks:
        # tick2 is the outer arc on polar axes; tick1 is the inner circle
        assert tick.tick2line.get_visible()
        assert not tick.tick1line.get_visible()
        assert tick.tick2line.get_markersize() == 5
        assert not tick.tick2line.get_clip_on()
        assert tick._tickdir == "out"


@pytest.mark.parametrize("kind", ["stacked", "heatmap"])
def test_no_compass_spokes_but_rings_kept(hourly, kind):
    ax = pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", kind=kind, cbar=False)

    assert not any(line.get_visible() for line in ax.xaxis.get_gridlines())
    assert all(line.get_visible() for line in ax.yaxis.get_gridlines())


def test_invalid_kind_raises(hourly):
    with pytest.raises(ValueError, match="kind"):
        pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", kind="pie")


def test_requires_numeric_columns(hourly):
    with pytest.raises(TypeError):
        pollutionroseplot(data=hourly, ws="ws", wd="timestamp", pollutant="pm25")


def test_draws_on_given_polar_axes(hourly):
    fig, (ax1, ax2) = plt.subplots(1, 2, subplot_kw={"projection": "polar"})
    plt.sca(ax2)

    ax = pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", ax=ax1)

    assert ax is ax1
    assert len(ax1.containers) > 0
    assert len(ax2.containers) == 0


def test_rejects_cartesian_axes(hourly):
    _, ax = plt.subplots()

    with pytest.raises(TypeError, match="polar"):
        pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", ax=ax)


def test_creates_polar_axes_on_fresh_figure(hourly):
    plt.figure()

    ax = pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25")

    assert ax.name == "polar"
    assert ax.figure.axes == [ax]


def test_faceted_argument_is_deprecated(hourly):
    with pytest.warns(FutureWarning, match="faceted"):
        pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", faceted=True)


@pytest.mark.parametrize("kind", ["stacked", "heatmap"])
def test_every_facet_gets_compass_labels(hourly, kind):
    df = hourly.assign(Month=hourly["timestamp"].dt.month_name())
    df = df[df["timestamp"].dt.month <= 4]

    g = sns.FacetGrid(df, col="Month", col_wrap=2, subplot_kws={"projection": "polar"}, despine=False)
    g.map_dataframe(pollutionroseplot, ws="ws", wd="wd", pollutant="pm25", kind=kind, cbar=False, vmin=0, vmax=40)
    g.figure.canvas.draw()

    assert g.axes.size == 4
    for ax in g.axes.flat:
        labels = [t for t in ax.get_xticklabels() if t.get_visible()]
        assert [t.get_text() for t in labels] == COMPASS
        if kind == "heatmap":
            assert any(t.get_visible() and t.get_text() for t in ax.get_yticklabels())
