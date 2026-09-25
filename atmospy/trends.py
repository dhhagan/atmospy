import math
import warnings

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .utils import (
    check_for_numeric_cols,
    check_for_timestamp_col
)

__all__ = ["dielplot", "calendarplot"]

@mpl.ticker.FuncFormatter
def custom_month_formatter(x, pos):
    return str(math.ceil(x))

def _add_colorbar(im, ax, cbar_kws=None, units=None, **defaults):
    """Attach a colorbar for `im` to `ax` without mutating the caller's `cbar_kws`."""
    kws = dict(defaults, **(cbar_kws or {}))

    cb = ax.figure.colorbar(im, ax=ax, **kws)
    cb.outline.set_visible(False)

    # keep the colorbar uncluttered regardless of orientation
    cb.locator = mpl.ticker.MaxNLocator(4)
    cb.update_ticks()

    if units:
        cb.set_label(units)

    return cb

def _yearplot(data, x, y, ax=None, agg="mean", cmap="crest",
              height=2, aspect=5, vmin=None, vmax=None,
              linecolor="white", linewidths=0, cbar=True, cbar_kws=None,
              units="", faceted=False, **kwargs):
    """Plot a full year of time series data on a heatmap by month.

    Columns are calendar weeks counted from the Monday on or before
    January 1, so every day of the year lands in exactly one cell no
    matter which weekday the year starts on and regardless of ISO
    week numbering.
    """
    if ax is None:
        ax = plt.gca()

        if not faceted:
            ax.figure.set_size_inches(height*aspect, height)

    # only a single year can be shown at once
    years = np.unique(data.index.year)
    year = int(years[0])
    if years.size > 1:
        warnings.warn(
            f"calendarplot with freq='day' shows a single year; plotting {year} "
            f"and ignoring {', '.join(str(y) for y in years[1:])}.",
            UserWarning, stacklevel=3,
        )
        data = data[data.index.year == year]

    # the grid starts on the Monday on or before Jan 1 and runs through Dec 31
    tz = data.index.tz
    jan1 = pd.Timestamp(year=year, month=1, day=1, tz=tz)
    dec31 = pd.Timestamp(year=year, month=12, day=31, tz=tz)
    grid_origin = jan1 - pd.Timedelta(days=jan1.weekday())
    n_weeks = (dec31 - grid_origin).days // 7 + 1

    day_offset = (data.index.normalize() - grid_origin).days
    cells = pd.DataFrame({
        "Day of Week": data.index.weekday,
        "Week": day_offset // 7,
        y: data[y].values,
    })

    # compute pivoted data
    pivot = cells.pivot_table(
        index="Day of Week",
        columns="Week",
        values=y,
        aggfunc=agg
    )

    # adjust the index to ensure we have a properly-sized array
    pivot = pivot.reindex(
        index=range(0, 7),
        columns=range(0, n_weeks)
    )

    # reverse the array along the yaxis so that Monday ends up at the top of the fig
    pivot = pivot[::-1]

    # set the min and max of the colorbar
    if vmin is None:
        vmin = np.nanmin(pivot.values)

    if vmax is None:
        vmax = np.nanmax(pivot.values)

    # plot the heatmap
    im = ax.pcolormesh(
        pivot,
        vmin=vmin, vmax=vmax, cmap=cmap,
        linewidth=linewidths, edgecolors=linecolor
    )

    # label each month at the center of the weeks it spans, with a small
    # tick marking each month boundary
    month_starts = [
        (pd.Timestamp(year=year, month=m, day=1, tz=tz) - grid_origin).days / 7
        for m in range(1, 13)
    ]
    bounds = month_starts + [n_weeks]
    centers = [(lo + hi) / 2 for lo, hi in zip(bounds[:-1], bounds[1:])]

    ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(centers))
    ax.xaxis.set_major_formatter(mpl.ticker.FixedFormatter([
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]))
    ax.xaxis.set_minor_locator(mpl.ticker.FixedLocator(bounds))
    ax.tick_params(axis="x", which="major", length=0)
    ax.tick_params(axis="x", which="minor", length=3)

    ax.yaxis.tick_right()
    ax.yaxis.set_major_locator(mpl.ticker.FixedLocator([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5]))
    ax.yaxis.set_major_formatter(mpl.ticker.FixedFormatter([
        "Sun", "Sat", "Fri", "Thu", "Wed", "Tue", "Mon"
    ]))
    ax.tick_params(axis="y", which="major", right=False, labelrotation=0)
    for label in ax.get_yticklabels():
        label.set_ha("left")
        label.set_va("center")

    # add a big ol' year on the left-hand side
    ax.set_ylabel(
        f"{year}",
        fontsize=28, color="gray", ha="center"
    )

    # add a colorbar if set
    if cbar:
        _add_colorbar(im, ax, cbar_kws, units, pad=0.05)

    return ax


def _monthplot(data, x, y, ax=None, agg="mean", height=3, aspect=1,
               vmin=None, vmax=None, cmap="crest", linewidths=0.1,
               linecolor="white", cbar=True, cbar_kws=None,
               units=None, faceted=False, **kwargs):
    """Plot a full month of time series data on a heatmap by hour.
    """
    if ax is None:
        ax = plt.gca()

        if not faceted:
            ax.figure.set_size_inches(height*aspect, height)

    # only a single calendar month can be shown at once
    year_month = data.index.year * 100 + data.index.month
    months = np.unique(year_month)
    if months.size > 1:
        def _fmt(ym):
            return f"{ym // 100}-{ym % 100:02d}"

        warnings.warn(
            f"calendarplot with freq='hour' shows a single month; plotting {_fmt(months[0])} "
            f"and ignoring {', '.join(_fmt(m) for m in months[1:])}.",
            UserWarning, stacklevel=3,
        )
        data = data[year_month == months[0]]

    # add pivot columns
    data = data.assign(**{
        "Day of Month": data.index.day,
        "Hour of Day": data.index.hour,
    })

    # compute the pivot data
    pivot = data.pivot_table(
        index="Hour of Day",
        columns="Day of Month",
        values=y,
        aggfunc=agg
    )

    # get the total number of available days in the month
    days_in_month = data.index.days_in_month[0]

    # adjust the index to ensure we have a properly-sized array
    pivot = pivot.reindex(
        index=range(0, 24),
        columns=range(1, days_in_month + 1)
    )

    # reverse the order of the matrix along the y-axis so that midnight is at the top
    pivot = pivot[::-1]

    # set the min and max values for the colorbar
    if vmin is None:
        vmin = np.nanmin(pivot.values)

    if vmax is None:
        vmax = np.nanmax(pivot.values)

    # plot the heatmap
    im = ax.pcolormesh(
        pivot,
        cmap=cmap, vmin=vmin, vmax=vmax,
        linewidth=linewidths, edgecolors=linecolor
    )

    # add a colorbar if set
    if cbar:
        _add_colorbar(im, ax, cbar_kws, units)

    # adjust the axes labels
    ax.xaxis.set_major_locator(mpl.ticker.FixedLocator([x - 0.5 for x in list(range(1, days_in_month, 4))]))
    ax.xaxis.set_major_formatter(custom_month_formatter)
    ax.set_yticks([0, 6, 12, 18, 24])
    ax.set_yticklabels([
        "12 AM", "6 PM", "12 PM", "6 AM", "12 AM"
    ])

    return ax


def calendarplot(data, x, y, freq="day", agg="mean", vmin=None, vmax=None, cmap="crest", 
                 ax=None, linecolor="white", linewidths=0, cbar=True, cbar_kws=None,
                 xlabel=None, ylabel=None, title=None, units="", height=2, 
                 aspect=5.0, faceted=False, **kwargs):
    """Visualize data as a heatmap on a monthly or annual basis.
    
    Calendar plots can be a useful way to visualize trends in data over longer periods 
    of time. This function is quite generic and allows you to visualize data either by 
    month (where the x-axis is day of month and y-axis is hour of day) or year (where 
    x-axis is the week of the year and y-axis is the day of the week). Configure the plot
    to aggregate the data any way you choose (e.g., sum, mean, max).
    
    Only a single month or single year can be shown at a time. If the data span
    more than one, the first is plotted and a warning lists what was ignored. To
    show several, set up a Seaborn FacetGrid and call calendarplot per facet.
    
    This function is heavily influenced by the `calplot <https://calplot.readthedocs.io/en/latest/>`_ 
    python library.
    
    Parameters
    ----------
    data : :class:`pandas.DataFrame`
        Tabular data as a pandas DataFrame.
    x : key in `data`
        Variable that corresponds to the timestamp column in `data`.
    y : key in `data`
        Variable that corresponds to the variable you would like to group and plot.
    freq : str, optional
        The frequency by which to average (one of [`hour`, `day`]), by default "day"
    agg : str, optional
        The function to aggregate by, by default "mean"
    vmin : float, optional
        The minimum value to color by, by default None
    vmax : float, optional
        The maximum value to color by, by default None
    cmap : str, optional
        The name of the colormap, by default "crest"
    ax : axes, optional
        A matplotlib axes object, by default None
    linecolor : str, optional
        The color of the inner lines, by default "white"
    linewidths : int, optional
        The width of the inner lines, by default 0
    cbar : bool, optional
        If true, add a colorbar, by default True
    cbar_kws : dict, optional
        A dictionary of kwargs to send along to the colorbar, by default None
    xlabel : str, optional
        The x-axis label, by default None
    ylabel : str, optional
        The y-axis label, by default None
    title : str, optional
        The figure title, by default None
    units : str, optional
        The units of the plotted item, used to label the colorbar, by default ""
    height : int, optional
        The figure height in inches, by default 2
    aspect : float, optional
        The aspect ratio of the figure, by default 5.0
    faceted : bool optional
        Set to `True` if combining with a FacetGrid, optional
    
    Returns
    -------
    :class:`matplotlib.axes._axes.Axes`

    Examples
    --------
    
    Plot a simple heatmap for the entire year.

    >>> df = atmospy.load_dataset("us-bc")
    >>> atmospy.calendarplot(df, x="Timestamp GMT", y="Sample Measurement")
    
    """
    check_for_timestamp_col(data, x)
    check_for_numeric_cols(data, [y])
    
    if freq not in ("hour", "day"):
        raise ValueError("Invalid argument for `freq`")
    
    cbar_kws_default = {
        "shrink": 0.67,
        "drawedges": False
    }
    
    if cbar_kws is None:
        cbar_kws = {}
        
    cbar_kws = dict(cbar_kws_default, **cbar_kws)
    
    # select only the data that is needed
    df = data[[x, y]].copy(deep=True)
    df = df.set_index(x)
    
    if freq == "day":
        ax = _yearplot(
            df, x, y, ax=ax,
            agg=agg, height=height, aspect=aspect,
            vmin=vmin, vmax=vmax, linewidths=linewidths, linecolor=linecolor,
            cbar=cbar, cbar_kws=cbar_kws, units=units, cmap=cmap, faceted=faceted, **kwargs
        )
    elif freq == "hour":
        ax = _monthplot(
            df, x, y, ax=ax,
            agg=agg, height=height, aspect=aspect,
            vmin=vmin, vmax=vmax, linewidths=linewidths, linecolor=linecolor,
            cbar=cbar, cbar_kws=cbar_kws, units=units, cmap=cmap, faceted=faceted, **kwargs
        )
    
    ax.set_aspect("equal")

    # remove the spines
    for spine in ("top", "bottom", "right", "left"):
        ax.spines[spine].set_visible(False)
        
    if title:
        ax.set_title(title)
    
    if xlabel:
        ax.set_xlabel(xlabel)
        
    if ylabel:
        ax.set_ylabel(ylabel)
    
    return ax


def dielplot(data=None, *, x=None, y=None, freq="1h", ax=None, ylim=None, xlabel=None,
             ylabel=None, title=None, color=None, show_iqr=True, plot_kws=None, **kwargs):
    """Plot the diel (e.g., diurnal) trend for a pollutant.

    Diel plots can be incredibly useful for understanding daily
    patterns of air pollutants. Every observation is assigned to a
    time-of-day bin of width `freq`, and the mean and interquartile
    range across all days are plotted for each bin. Data need not be
    evenly spaced; bins with no observations are left as gaps.

    Parameters
    ----------
    data : :class:`pandas.DataFrame`
        Tabular data as a pandas DataFrame.
    x : key in `data`
        Variable that corresponds to the timestamp in `data`.
    y : key in `data`
        Variable that corresponds to the pollutant of interest.
    freq : str or pandas offset, optional
        The width of each time-of-day bin. Must divide evenly into
        24 hours (e.g., "1h", "30min", "15min"), by default "1h"
    ax : :class:`matplotlib.axes._axes.Axes`, optional
        An axis to plot on; if not defined, one will be created, by default None
    ylim : tuple of floats, optional
        A tuple describing (ymin, ymax), by default None
    xlabel : str, optional
        The label for the x-axis, by default None
    ylabel : str, optional
        The label for the y-axis, by default None
    title : str, optional
        The title for the plot, by default None
    color : str, optional
        Specify the color to use in the figure
    show_iqr : bool, optional
        If True, plot the interquartile range as a shaded region, default True
    plot_kws : dict or None, optional
        Additional keyword arguments are passed directly to the underlying
        plot call, by default None

    Returns
    -------
    :class:`matplotlib.axes._axes.Axes`


    Examples
    --------

    Plot the diel trend of ozone at hourly resolution.

    >>> df = atmospy.load_dataset("us-ozone")
    >>> atmospy.dielplot(data=df, x="Timestamp Local", y="Sample Measurement")

    Use finer bins if your data supports it.

    >>> atmospy.dielplot(data=df, x="Timestamp Local", y="Sample Measurement", freq="15min")

    """
    default_plot_kws = {
        "lw": 3,
    }

    # complete some initial data quality checks
    check_for_timestamp_col(data, x)
    check_for_numeric_cols(data, [y])

    # validate the bin width: it must be a fixed duration that divides a day evenly
    try:
        step = pd.Timedelta(pd.tseries.frequencies.to_offset(freq))
    except (ValueError, TypeError):
        raise ValueError(
            f"`freq` must be a fixed duration such as '1h' or '15min'; got {freq!r}."
        ) from None

    day = pd.Timedelta(hours=24)
    if not pd.Timedelta(0) < step < day or day % step != pd.Timedelta(0):
        raise ValueError(
            f"`freq` must be shorter than 24 hours and divide evenly into it; got {freq!r}."
        )

    # merge the user's plot kwargs over the defaults
    plot_kws = dict(default_plot_kws, **(plot_kws or {}))
    if color is not None:
        plot_kws["c"] = color

    # figure setup
    if ax is None:
        ax = plt.gca()

    # assign each observation to a time-of-day bin
    timestamps = data[x]
    floored = timestamps.dt.floor(step)
    time_of_day = floored - floored.dt.normalize()

    _data = pd.DataFrame({"time_of_day": time_of_day.values, y: data[y].values})

    # compute the diel statistics per bin
    grouped = _data.groupby("time_of_day")[y]
    stats = pd.DataFrame({
        "mean": grouped.mean(),
        "q25": grouped.quantile(0.25),
        "q75": grouped.quantile(0.75),
    })

    # make sure every bin is present so gaps show as gaps, then wrap the
    # first bin around to 24:00 so the first and last points are identical
    bins = pd.timedelta_range(start=0, end=day, freq=step, closed="left")
    stats = stats.reindex(bins)
    stats.loc[day] = stats.iloc[0]

    # build a datetime index on an arbitrary day so matplotlib can format the axis
    origin = pd.Timestamp("2020-01-01")
    figure_index = origin + stats.index

    # plot the diel average
    ax.plot(figure_index, stats["mean"], **plot_kws)

    # add the IQR as a shaded region
    if show_iqr:
        ax.fill_between(
            figure_index,
            y1=stats["q25"],
            y2=stats["q75"],
            alpha=0.25,
            lw=2,
            color=ax.lines[-1].get_color()
        )

    # adjust plot parameters
    ax.set_xlim(origin, origin + day)
    ax.xaxis.set_major_locator(mpl.dates.HourLocator(byhour=[0, 6, 12, 18]))
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%I:%M\n%p"))
    ax.xaxis.set_minor_locator(mpl.dates.HourLocator(interval=1))

    # add optional labels
    if xlabel:
        ax.set_xlabel(xlabel)

    if ylabel:
        ax.set_ylabel(ylabel)

    if title:
        ax.set_title(title)

    if ylim:
        ax.set_ylim(ylim)

    return ax
