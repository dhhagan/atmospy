"""Wind and pollution rose figures."""
import re
import warnings

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.collections import PatchCollection
from matplotlib.patches import PathPatch
from matplotlib.path import Path

from ._base import _add_colorbar
from .utils import check_for_numeric_cols

__all__ = ["pollutionroseplot"]

_COMPASS_LABELS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
_KINDS = ("stacked", "heatmap")
_AGG_NAMES = ("mean", "median", "min", "max", "std", "count")
_PERCENTILE = re.compile(r"^p(\d{1,3}(?:\.\d+)?)$")


def _ordinal(q):
    """Format a percentile value as an ordinal, e.g. 95 -> '95th', 91 -> '91st', 2.5 -> '2.5th'."""
    text = f"{q:g}"
    if not text.replace(".", "").isdigit() or "." in text:
        return f"{text}th"

    n = int(text)
    if n % 100 in (11, 12, 13):
        return f"{text}th"
    return text + {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def _resolve_agg(agg):
    """Turn the `agg` argument into a reducer plus a human-readable name for labels.

    Returns ``(func, name, has_units)``: `func` is what pandas ``agg`` will be
    given, `name` describes the statistic (empty when unknown, e.g. a lambda),
    and `has_units` is False for statistics that are not in the pollutant's
    units, such as a count.
    """
    if callable(agg):
        name = getattr(agg, "__name__", "")
        if name == "<lambda>":
            name = ""
        return agg, name, True

    if isinstance(agg, str):
        if agg in _AGG_NAMES:
            label = {"std": "std. dev."}.get(agg, agg)
            return agg, label, agg != "count"

        match = _PERCENTILE.match(agg)
        if match:
            q = float(match.group(1))
            if 0.0 <= q <= 100.0:
                return (lambda s: s.quantile(q / 100.0)), f"{_ordinal(q)} percentile", True

    raise ValueError(
        f"`agg` must be one of {_AGG_NAMES}, a percentile such as 'p95', "
        f"or a callable; got {agg!r}."
    )


def _colorbar_label(agg_name, has_units, suffix):
    """Combine the statistic name and units into a colorbar label."""
    units = suffix if (has_units and suffix) else ""
    if agg_name and units:
        return f"{agg_name} ({units})"
    return agg_name or units


def _resolve_polar_axes(ax):
    """Return a polar axes to draw on, creating one if needed."""
    if ax is None:
        fig = plt.gcf()

        # inside a FacetGrid the current axes is already the polar facet
        if fig.axes and fig.gca().name == "polar":
            return fig.gca()

        return fig.add_subplot(111, projection="polar")

    if ax.name != "polar":
        raise TypeError(
            "pollutionroseplot needs a polar axes; create one with "
            "`fig.add_subplot(projection='polar')` or, on a FacetGrid, "
            "`subplot_kws={'projection': 'polar'}`."
        )

    return ax


def _style_compass(ax):
    """Orient the axes like a compass and label every panel, even on a shared grid."""
    ax.set_theta_direction("clockwise")
    ax.set_theta_zero_location("N")

    ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(np.radians(np.arange(0, 360, 45))))
    ax.xaxis.set_major_formatter(mpl.ticker.FixedFormatter(_COMPASS_LABELS))

    # seaborn's FacetGrid hides the "inner" tick labels of shared axes, which is
    # right for cartesian grids but leaves most roses without a compass
    ax.tick_params(axis="x", labelbottom=True)
    ax.tick_params(axis="y", labelleft=True)

    # no spokes from the center to the compass points; the rings carry the scale
    ax.xaxis.grid(False)

    # outward tick marks on the outer circle at each compass point. polar axes
    # hide theta tick marks by default, and `top` is the outer arc
    spine = ax.spines["polar"]
    ax.tick_params(
        axis="x", which="major", bottom=False, top=True, direction="out",
        length=5, width=spine.get_linewidth(), color=spine.get_edgecolor(), pad=6,
    )
    for tick in ax.xaxis.get_major_ticks():
        tick.tick2line.set_clip_on(False)


def _bin_edges(bins, name):
    """Validate user-supplied bin edges and return them as a float array."""
    edges = np.asarray(bins, dtype=float).ravel()

    if edges.size < 2:
        raise ValueError(f"`{name}` needs at least two edges; got {bins!r}.")

    if not np.all(np.diff(edges) > 0):
        raise ValueError(f"`{name}` must be strictly increasing; got {bins!r}.")

    return edges


def _pollutant_bin_labels(edges, suffix):
    labels = []
    for lower, upper in zip(edges[:-1], edges[1:]):
        if np.isinf(upper):
            labels.append(f"≥{lower:g} {suffix}".rstrip())
        else:
            labels.append(f"{lower:g} to {upper:g} {suffix}".rstrip())

    return labels


#: Default wind speed ring edges for the heatmap: 1 m/s rings from 0 to 15 m/s.
DEFAULT_WS_BINS = np.arange(0.0, 16.0, 1.0)


def _major_rings(edges, max_lines=3):
    """Pick the ring edges that get a gridline and a label.

    Every `k`-th edge is kept, with `k` chosen so at most `max_lines` rings
    are marked, and the outer edge is always included and labeled as
    open-ended. Returns the edge positions and their labels.
    """
    n_rings = edges.size - 1

    # smallest step that fits within max_lines, preferring one that divides the
    # rings evenly so the marked edges are evenly spaced
    smallest = max(1, -(-n_rings // max_lines))
    every = next(
        (k for k in range(smallest, n_rings // 2 + 1) if n_rings % k == 0),
        smallest,
    )

    positions, labels = [], []
    for i in range(every, n_rings, every):
        positions.append(edges[i])
        labels.append(f"{edges[i]:g}")

    positions.append(edges[-1])
    labels.append(f"≥{edges[-1]:g}")

    return positions, labels


def _polar_cells(ax, theta_edges, r_edges, grid, cmap, vmin, vmax, lw):
    """Draw a (rings x sectors) grid of colormapped cells with properly curved arcs.

    `pcolormesh` only transforms cell corners, so on polar axes every arc
    becomes a straight chord. Building each cell as a path with arc
    interpolation enabled keeps the edges round. Cells are ordered ring-major,
    sector-minor, so the collection's array reshapes back to `grid`.
    """
    grid = np.asarray(grid, dtype=float)
    n_rings, n_sectors = grid.shape
    codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]

    patches = []
    for i in range(n_rings):
        r0, r1 = r_edges[i], r_edges[i + 1]
        for j in range(n_sectors):
            t0, t1 = theta_edges[j], theta_edges[j + 1]
            verts = [(t0, r0), (t1, r0), (t1, r1), (t0, r1), (t0, r0)]
            patches.append(PathPatch(Path(verts, codes, _interpolation_steps=32)))

    values = np.ma.masked_invalid(grid.ravel())

    cells = PatchCollection(patches, cmap=cmap, transform=ax.transData)
    cells.set_array(values)
    cells.set_clim(vmin, vmax)
    cells.set_edgecolors(np.where(np.ma.getmaskarray(values), "none", "white"))
    cells.set_linewidths(lw)
    ax.add_collection(cells)

    return cells


def _direction_segments(wd, segments):
    """Assign each wind direction to one of `segments` sectors centered on north.

    Returns the sector index per record and the sector edges in degrees,
    starting half a sector west of north so the first sector straddles 0°.
    """
    step = 360.0 / segments
    shifted = (np.asarray(wd, dtype=float) + step / 2.0) % 360.0
    index = np.floor(shifted / step).astype(int)
    edges = np.arange(segments + 1) * step - step / 2.0

    return index, edges


def pollutionroseplot(data=None, *, ws=None, wd=None, pollutant=None, kind="stacked",
                      segments=12, bins=(0, 10, 100, 1000), suffix="a.u.", calm=0.0,
                      lw=1, legend=True, palette="flare",
                      ws_bins=None, agg="mean", min_count=1, cmap="viridis",
                      vmin=None, vmax=None, cbar=True, cbar_kws=None,
                      title=None, ax=None, faceted=None, **kwargs):
    """Plot the intensity and directionality of a pollutant on a polar plot.

    Two kinds of rose are available:

    ``kind="stacked"``
        The classic pollution rose, a modified version of
        `Phil Hobson's work <https://gist.github.com/phobson/41b41bdd157a2bcf6e14>`_.
        Each direction sector is a bar whose length is the percentage of
        records with wind from that direction, stacked by pollutant
        concentration bin (`bins`). It shows *where the wind comes from*
        and *how polluted it is when it does*.

    ``kind="heatmap"``
        Records are cut by both wind direction (`segments`) and wind speed
        (`ws_bins`), and each direction-by-speed cell is colored by the
        aggregated pollutant value in that cell (`agg`). It shows *which
        combinations of direction and speed bring pollution*, which helps
        separate local sources (high at low speed) from transported ones
        (high at high speed).

    Wind direction sectors are centered on the compass points, so with the
    default 12 segments the first sector spans 345° to 15°.

    Parameters
    ----------
    data : :class:`pandas.DataFrame`
        Tabular data as a pandas DataFrame.
    ws : key in `data`
        Variable that corresponds to the wind speed data in `data`.
    wd : key in `data`
        Variable that corresponds to the wind direction data in `data`, in
        degrees clockwise from north.
    pollutant : key in `data`
        Variable that corresponds to the pollutant of interest in `data`.
    kind : {"stacked", "heatmap"}, optional
        Which rose to draw, by default "stacked"
    segments : int, optional
        The number of wind direction sectors, by default 12
    bins : sequence of floats, optional
        Pollutant concentration bin edges for the stacked rose. Bins are
        closed on the left, so a value equal to an edge falls in the bin
        above it. If the last edge is not `inf` a catch-all bin is added,
        by default (0, 10, 100, 1000)
    suffix : str, optional
        The units of `pollutant`, used in the legend of the stacked rose and,
        together with the name of the statistic (e.g. "mean (ppb)" or
        "95th percentile (ppb)"), on the colorbar of the heatmap,
        by default "a.u."
    calm : float, optional
        Wind speeds at or below this value are treated as calm. Calm records
        are excluded from the sectors; on the stacked rose they are shown as
        the blank hole in the center, whose radius is their share of all
        records, by default 0.
    lw : float, optional
        Line width of the edges drawn between bars or cells, by default 1
    legend : bool, optional
        If `True`, add a legend to the stacked rose, by default True
    palette : str, optional
        Seaborn palette for the concentration bins of the stacked rose,
        by default "flare"
    ws_bins : sequence of floats, optional
        Wind speed bin edges for the heatmap rings. Speeds above the last
        edge are included in the outermost ring. If `None`, 1 m/s rings
        from 0 to 15 m/s are used, by default None
    agg : str or callable, optional
        How to aggregate `pollutant` within each heatmap cell. One of
        "mean", "median", "min", "max", "std", or "count"; a percentile
        written as "p95" (any value from "p0" to "p100"); or a callable
        that reduces a :class:`pandas.Series` to a single number,
        by default "mean"
    min_count : int, optional
        Heatmap cells with fewer records than this are left blank,
        by default 1
    cmap : str or colormap, optional
        Colormap for the heatmap, by default "viridis"
    vmin, vmax : float, optional
        Color limits for the heatmap. Cells beyond a limit are drawn in the
        end color and the colorbar grows a pointed cap to show values were
        clipped. Set them explicitly when faceting so every panel shares a
        scale, by default None
    cbar : bool, optional
        If `True`, add a colorbar to the heatmap, by default True
    cbar_kws : dict, optional
        Keyword arguments for the colorbar, by default None
    title : str, optional
        Set the figure title, by default None
    ax : :class:`matplotlib.projections.polar.PolarAxes`, optional
        A polar axes to draw on. If `None`, the current axes is used when it
        is polar (as inside a FacetGrid), otherwise one is created,
        by default None
    faceted : bool, optional
        Deprecated and ignored; faceting is detected automatically.

    Returns
    -------
    :class:`matplotlib.projections.polar.PolarAxes`

    Examples
    --------
    Using defaults, plot the pollution rose for PM2.5:

    >>> df = atmospy.load_dataset("air-sensors-met")
    >>> atmospy.pollutionroseplot(data=df, ws="ws", wd="wd", pollutant="pm25")

    Show mean PM2.5 by wind direction and speed instead:

    >>> atmospy.pollutionroseplot(
    ...     data=df, ws="ws", wd="wd", pollutant="pm25", kind="heatmap", suffix="µg/m³"
    ... )

    """
    check_for_numeric_cols(data, [ws, wd, pollutant])

    if kind not in _KINDS:
        raise ValueError(f"`kind` must be one of {_KINDS}; got {kind!r}.")

    agg_func, agg_name, agg_has_units = _resolve_agg(agg)

    if faceted is not None:
        warnings.warn(
            "The `faceted` argument of pollutionroseplot is deprecated and ignored; "
            "faceting is now detected automatically.",
            FutureWarning, stacklevel=2,
        )

    ax = _resolve_polar_axes(ax)

    # keep only complete records, then split calm from blowing
    valid = data[[ws, wd, pollutant]].dropna()
    blowing = valid[valid[ws] > calm]
    n_total = len(valid)
    pct_calm = 100.0 * (1.0 - len(blowing) / n_total) if n_total else 0.0

    sector, sector_edges = _direction_segments(blowing[wd], segments)
    step = 360.0 / segments

    if kind == "stacked":
        edges = _bin_edges(bins, "bins")
        if not np.isinf(edges[-1]):
            edges = np.append(edges, np.inf)

        labels = _pollutant_bin_labels(edges, suffix)
        conc = pd.cut(blowing[pollutant], bins=edges, right=False, labels=labels)

        # percent of all valid records in each (sector, concentration bin)
        pct = (
            pd.DataFrame({"sector": sector, "conc": conc})
            .groupby(["sector", "conc"], observed=False)
            .size()
            .unstack("conc")
            .reindex(index=range(segments), columns=labels, fill_value=0)
            .mul(100.0 / n_total if n_total else 0.0)
        )

        colors = sns.color_palette(palette, n_colors=len(labels))
        theta = np.radians(np.arange(segments) * step)
        width = np.radians(step)

        bottom = np.zeros(segments)
        for color, label in zip(colors, labels):
            height = pct[label].to_numpy()
            ax.bar(theta, height, width=width, bottom=bottom, label=label,
                   color=color, edgecolor="white", linewidth=lw)
            bottom = bottom + height

        # at most three labeled percent rings, on round numbers, inside the tallest bar
        r_max = float(bottom.max()) if bottom.size and bottom.max() > 0 else 1.0
        ticks = mpl.ticker.MaxNLocator(nbins=3, steps=[1, 2, 2.5, 5, 10]).tick_values(0, r_max)
        ticks = ticks[(ticks > 0) & (ticks <= r_max)]
        ax.set_ylim(0, r_max * 1.05)
        ax.yaxis.set_major_locator(mpl.ticker.FixedLocator(ticks))
        ax.yaxis.set_major_formatter(mpl.ticker.FixedFormatter([f"{t:g}%" for t in ticks]))

        # calm records are the hole in the center: its radius is their share of the total
        calm_fraction = min(pct_calm / 100.0, 0.9)
        ax.set_rorigin(-calm_fraction * ax.get_ylim()[1] / (1.0 - calm_fraction))

        if legend:
            ax.legend(
                loc="center left",
                handlelength=1,
                handleheight=1,
                bbox_to_anchor=(1.1, 0, 0.5, 1),
            )

        _style_compass(ax)
        ax.set_rlabel_position(22.5)
        ax.tick_params(axis="y", labelsize="small")
        for label in ax.get_yticklabels():
            label.set_bbox({"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1})

    else:
        if ws_bins is None:
            r_edges = DEFAULT_WS_BINS.copy()
        else:
            r_edges = _bin_edges(ws_bins, "ws_bins")

        n_rings = r_edges.size - 1

        # speeds above the outer edge belong to the outermost ring
        speed = np.clip(blowing[ws].to_numpy(), r_edges[0], np.nextafter(r_edges[-1], -np.inf))
        ring = np.searchsorted(r_edges, speed, side="right") - 1
        ring = np.clip(ring, 0, n_rings - 1)

        grouped = (
            pd.DataFrame({"sector": sector, "ring": ring, "value": blowing[pollutant].to_numpy()})
            .groupby(["sector", "ring"])["value"]
        )
        cells = grouped.agg(agg_func)
        cells[grouped.size() < min_count] = np.nan

        grid = (
            cells
            .unstack("sector")
            .reindex(index=range(n_rings), columns=range(segments))
            .to_numpy()
        )

        mesh = _polar_cells(ax, np.radians(sector_edges), r_edges, grid, cmap, vmin, vmax, lw)

        if cbar:
            _add_colorbar(
                mesh, ax, cbar_kws, _colorbar_label(agg_name, agg_has_units, suffix),
                values=grid, pad=0.1, shrink=0.75,
            )

        _style_compass(ax)

        # label the rings by wind speed, marking the outer ring as open-ended
        ax.set_ylim(0, r_edges[-1])
        positions, labels = _major_rings(r_edges)
        ax.yaxis.set_major_locator(mpl.ticker.FixedLocator(positions))
        ax.yaxis.set_major_formatter(mpl.ticker.FixedFormatter(labels))
        ax.set_rlabel_position(22.5)
        ax.tick_params(axis="y", labelsize="small")
        for label in ax.get_yticklabels():
            label.set_bbox({"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1})

    if title:
        ax.set_title(title)

    return ax
