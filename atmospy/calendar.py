"""This file will contain figures for:

  1. Calendar
  2. straight line calendar thing like Sentry?
"""
from .utils import (
    remove_na,
)
from seaborn import (
    FacetGrid,
)
from atmospy.utils import (
    check_for_numeric_cols,
    check_for_timestamp_col
)
import numpy as np
import math
import matplotlib as mpl
import matplotlib.pyplot as plt

__all__ = ["calendarplot", ]

@mpl.ticker.FuncFormatter
def custom_month_formatter(x, pos):
    return str(math.ceil(x))


def _yearplot(data, x, y, ax=None, agg="mean", cmap="crest", 
              height=2, aspect=5, vmin=None, vmax=None,
              linecolor="white", linewidths=0, cbar=True, cbar_kws=None, units=""):
    """Plot a full year of time series data on a heatmap by month.
    """
    if ax is None:
        ax = plt.gca()
        ax.figure.set_size_inches(height*aspect, height)
        
    # if more than 1Y of data was provided, limit to 1Y
    years = np.unique(data.index.year)
    if years.size > 1:
        # warn
        data = data[data.index.year == years[0]]
        
    data["Day of Week"] = data.index.weekday
    data["Week of Year"] = data.index.isocalendar().week
    
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
               linecolor="white", cbar=True, cbar_kws=None, units=None):
    """Plot a full month of time series data on a heatmap by hour.
    """
    if ax is None:
        ax = plt.gca()
        ax.figure.set_size_inches(height*aspect, height)
        
    # if more than 1mo of data was provided, limit to 1mo
    months = np.unique(data.index.month)
    if months.size > 1:
        # TODO: log warning
        data = data[data.index.month == months[0]]
        
    # add pivot columns
    data["Day of Month"] = data.index.day
    data["Hour of Day"] = data.index.hour
    
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
                 xlabel=None, ylabel=None, title=None, units="", height=2, aspect=5.0):
    """Create a heatmap from time series data.
    
    Parameters
    ----------
    data : pd.DataFrame
        Dataframe containing the data of interest.
    x : str
        The name of the datetime column.
    y : str
        The name of the data column.
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
        
    Examples
    --------
    
    Returns
    -------
    ax : axes object
        TODO: Fill this out.
    
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
            cbar=cbar, cbar_kws=cbar_kws, units=units, cmap=cmap
        )
    elif freq == "hour":
        ax = _monthplot(
            df, x, y,
            agg=agg, height=height, aspect=aspect,
            vmin=vmin, vmax=vmax, linewidths=linewidths, linecolor=linecolor,
            cbar=cbar, cbar_kws=cbar_kws, units=units, cmap=cmap
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