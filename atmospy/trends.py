import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import math
from .utils import (
    check_for_numeric_cols,
    check_for_timestamp_col
)

# Turn off chained assignment warnings
pd.options.mode.chained_assignment = None

__all__ = ["dielplot", "calendarplot"]

@mpl.ticker.FuncFormatter
def custom_month_formatter(x, pos):
    return str(math.ceil(x))

def _yearplot(data, x, y, ax=None, agg="mean", cmap="crest", 
              height=2, aspect=5, vmin=None, vmax=None,
              linecolor="white", linewidths=0, cbar=True, cbar_kws=None, 
              units="", faceted=False, **kwargs):
    """Plot a full year of time series data on a heatmap by month.
    """
    if ax is None:
        ax = plt.gca()
        
        if not faceted:
            ax.figure.set_size_inches(height*aspect, height)
        
    # if more than 1Y of data was provided, limit to 1Y
    years = np.unique(data.index.year)
    if years.size > 1:
        # warn
        data = data[data.index.year == years[0]]
        
    data.loc[:, "Day of Week"] = data.index.weekday
    data.loc[:, "Week of Year"] = data.index.isocalendar().week
    
    # compute pivoted data
    pivot = data.pivot_table(
        index="Day of Week", 
        columns="Week of Year", 
        values=y, 
        aggfunc=agg
    )
    
    # adjust the index to ensure we have a properly-sized array
    pivot = pivot.reindex(
        index=range(0, 7),
        columns=range(1, 53)
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
    
    # modify the axes ticks
    ax.xaxis.set_major_locator(mpl.ticker.LinearLocator(14))
    ax.xaxis.set_ticklabels([
        "",
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ""
    ], rotation="horizontal", va="center")
    
    ax.yaxis.tick_right()
    ax.yaxis.set_ticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
    ax.yaxis.set_ticklabels([
        "Sun", "Sat", "Fri", "Thu", "Wed", "Tue", "Mon"
    ], rotation="horizontal", va="center", ha="left")
    ax.yaxis.set_tick_params(right=False)
    
    # add a big ol' year on the left-hand side
    ax.set_ylabel(
        f"{years[0]}",
        fontsize=28, color="gray", ha="center"
    )
    
    # add a colorbar if set
    if cbar:
        cbar_kws["pad"] = cbar_kws.get("pad", 0.05)

        cb = ax.figure.colorbar(im, ax=ax, **cbar_kws)
        cb.outline.set_visible(False)
        
        # adjust the colorbar ticklabels
        cb.ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(4))
        
        # modify the tick labels
        # TODO: this is currently not working
        ticklabels = [x.get_text() for x in cb.ax.get_yticklabels()]
        ticklabels[-1] = f"{ticklabels[-1]} {units}"
        cb.set_ticks(cb.get_ticks())
        cb.set_ticklabels(ticklabels)
    
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
        
    # if more than 1mo of data was provided, limit to 1mo
    months = np.unique(data.index.month)
    if months.size > 1:
        # TODO: log warning
        data = data[data.index.month == months[0]]
        
    # add pivot columns
    data.loc[:, "Day of Month"] = data.index.day
    data.loc[:, "Hour of Day"] = data.index.hour
    
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
    
    # reverse the order of the matrix along the y-axis so that Monday is at the top
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
        cb = ax.figure.colorbar(im, ax=ax, **cbar_kws)
        cb.outline.set_visible(False)
        
        # adjust the tick labels
        ticklabels = [x.get_text() for x in cb.ax.get_yticklabels()]
        ticklabels[-1] = f"{ticklabels[-1]} {units}"
        cb.set_ticks(cb.get_ticks())
        cb.set_ticklabels(ticklabels)
        
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
    to aggregrate the data any way you choose (e.g., sum, mean, max).
    
    Currently, you can only plot a single month or single year at a time depending on 
    configuration. To facet these, please set up a Seaborn FacetGrid and call the 
    calendarplot separately.
    
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
        The units of the plotted item for labeling purposes only, by default ""
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
            df, x, y,
            agg=agg, height=height, aspect=aspect,
            vmin=vmin, vmax=vmax, linewidths=linewidths, linecolor=linecolor,
            cbar=cbar, cbar_kws=cbar_kws, units=units, cmap=cmap, faceted=faceted, **kwargs
        )
    elif freq == "hour":
        ax = _monthplot(
            df, x, y,
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


def dielplot(data=None, *, x=None, y=None, ax=None, ylim=None, xlabel=None, 
             ylabel=None, title=None, color=None, show_iqr=True, plot_kws=None, **kwargs):
    """Plot the diel (e.g., diurnal) trend for a pollutant.
    
    Diel plots can be incredibly useful for understanding daily 
    patterns of air pollutants.

    Parameters
    ----------
    data : :class:`pandas.DataFrame`
        Tabular data as a pandas DataFrame.
    x : key in `data`
        Variable that corresponds to the timestamp in `data`.
    y : key in `data`
        Variable that corresponds to the pollutant of interest.
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
    shoq_iqr : bool, optional
        If True, plot the interquartile range as a shaded region, default True
    plot_kws : dict or None, optional
        Additional keyword arguments are passed directly to the underlying plot call
        , by default None
        
    Returns
    -------
    :class:`matplotlib.axes._axes.Axes`

        
    Examples
    --------
    
    Plot a simple heatmap for the entire year.

    >>> df = atmospy.load_dataset("us-bc")
    >>> atmospy.dielplot(data=df, x="Timestamp GMT", y="Sample Measurement")
    
    """
    default_plot_kws = {
        "lw": 3,
    }
    
    # complete some initial data quality checks
    check_for_timestamp_col(data, x)
    check_for_numeric_cols(data, [y])
    
    # 
    plot_kws = {} if plot_kws is None else dict(default_plot_kws, **plot_kws)
    if color is not None:
        plot_kws.update(dict(c=color))
    
    # copy over only the needed data
    _data = data[[x, y]].copy(deep=True)
    _data = _data.set_index(x)
    
    # 
    # figure setup
    if ax is None:
        ax = plt.gca()
        
    # compute the diel statistics
    stats = _data.groupby([_data.index.hour, _data.index.minute], as_index=False).describe()
    
    # append the first record so the first and last records are identical
    stats.loc[len(stats.index)] = stats.loc[0]
    
    # build an index we can use to make the figure
    index = stats.index.values
    freq = int(60 / ((index.size - 1) / 24))
    figure_index = pd.date_range(start='2020-01-01', periods=index.size, freq=f"{freq}min")
    
    # plot the diel average
    ax.plot(figure_index, stats[y]['mean'], **plot_kws)
    
    # add the IQR as a shaded region
    if show_iqr:
        ax.fill_between(
            figure_index,
            y1=stats[y]['25%'],
            y2=stats[y]['75%'],
            alpha=0.25,
            lw=2,
            color=plt.gca().lines[-1].get_color()
        )
    
    # adjust plot parameters
    xticks = ax.get_xticks()
    ax.set_xticks(np.linspace(xticks[0], xticks[-1], 5))
    ax.set(xlim=(xticks[0], xticks[-1]))
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