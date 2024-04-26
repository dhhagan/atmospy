"""This file contains the wind and pollution rose figures."""
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from .utils import (
    check_for_numeric_cols,
)

# Turn off chained assignment warnings
pd.options.mode.chained_assignment = None

__all__ = ["pollutionroseplot"]

def pollutionroseplot(data=None, *, ws=None, wd=None, pollutant=None, 
                      faceted=False, segments=12, bins=[0, 10, 100, 1000], suffix="a.u.",
                      calm=0., lw=1, legend=True, palette="flare",
                      title=None, **kwargs):
    """Plot the intensity and directionality of a variable on a traditional wind-rose plot.

    This function is a modified version of `Phil Hobson's work <https://gist.github.com/phobson/41b41bdd157a2bcf6e14>`_.

    Traditionally, a wind rose plots wind speed and direction so that you can see from what 
    direction is the wind coming from and at what velocity. For air quality purposes, we 
    often wonder whether or not there is directionality to the intensity of a certain 
    air pollutant. Well, look no further. This plot allows you to easily visualize the 
    directionality of a pollutant.
    
    Parameters
    ----------
    data : :class:`pandas.DataFrame`
        Tabular data as a pandas DataFrame.
    ws : key in `data`
        Variable that corresponds to the wind speed data in `data`.
    wd : key in `data`
        Variable that corresponds to the wind direction data in `data`.
    pollutant : key in `data`
        Variable that corresponds to the pollutant of interest in `data`.
    faceted : bool, optional
        Set to `True` if plotting on a FacetGrid, by default False
    segments : int, optional
        The number of bins along the theta axis to group by wind direction
        , by default 12
    bins : list or array of floats, optional
        An array of floats corresponding to the bin boundaries
        for `pollutant`; if the last entry is not inf, it will be 
        automatically added, by default [0, 10, 100, 1000]
    suffix : str, optional
        The suffix (or units) to use on the labels for `pollutant`, by default "a.u."
    calm : float, optional
        Set the definition of calm conditions; data under calm winds 
        will not be used to compute the statistics and 
        will be shown on the plot as blank in the center, by default 0.
    lw : int, optional
        Set the line width, by default 1
    legend : bool, optional
        If `True` a legend will be added to the figure, by default True
    palette : str, optional
        Select the color palette to use, by default "flare"
    title : str, optional
        Set the figure title, by default None
        
    Returns
    -------
    :class:`matplotlib.axes._axes.Axes`
    
    Examples
    --------
    Using defaults, plot the pollution rose for PM2.5:
    
    >>> df = atmospy.load_dataset("air-sensors-met")
    >>> atmospy.pollutionroseplot(data=df, ws="ws", wd="wd", pollutant="pm25")
    
    """
    check_for_numeric_cols(data, [ws, wd, pollutant])

    # if the bins don't end in inf, add it
    if not np.isinf(bins[-1]):
        bins.append(np.inf)
        
    # 
    bins = np.asarray(bins)
    
    # setup the color palette
    cp = sns.color_palette(palette, n_colors=bins.shape[0]-1)
    
    # convert the number of segments into the wind bins
    wd_segments = np.linspace(0, 360, segments+1)
    
    def _cat_pollutant_labels(bins, suffix):
        """_summary_

        Parameters
        ----------
        bins : _type_
            _description_
        suffix : _type_
            _description_
        """
        list_of_labels = list()
        for lowerbound, upperbound in zip(bins[:-1], bins[1:]):
            if np.isinf(upperbound):
                list_of_labels.append(f">{lowerbound:.0f} {suffix}")
            else:
                list_of_labels.append(f"{lowerbound:.0f} to {upperbound:.0f} {suffix}")
                
        return list_of_labels
    
    def _compute_bar_dims(thetas):
        thetas = (thetas[:-1] + thetas[1:]) / 2.
        
        midpoints = [math.radians(theta) for theta in thetas]
        width = math.radians(360./thetas.shape[0])
        
        return midpoints, width
    
    # compute the percentage of calm datapoints
    # where calm is anything with a windspeed < `calm`
    pct_calm = 100*data[data[ws] <= calm].shape[0] / data.shape[0]
    
    # group the data by bin and normalize
    rv = (
        data[data[ws] > calm]
        .assign(
            _cp=lambda x: pd.cut(
                data[pollutant], 
                bins=bins, 
                right=True,
                labels=_cat_pollutant_labels(bins, suffix)
            )
        )
        .assign(
            _wb=lambda x: pd.cut(
                data[wd],
                bins=wd_segments,
                right=True,
                labels=(wd_segments[:-1]+wd_segments[1:])/2.
            )
        )
        .groupby(["_cp", "_wb"])
        .size()
        .unstack(level="_cp")
        .fillna(0.)
        .sort_index(axis=1)
        .applymap(lambda x: 100 * x / data.shape[0])
    )
    
    # compute the bar dims
    bar_midpoints, bar_width = _compute_bar_dims(wd_segments)
    
    # if plotting onto a FacetGrid, get the current axis, otherwise create one
    if faceted:
        ax = plt.gca()
    else:
        fig = plt.gcf()
        ax = fig.add_subplot(111, projection='polar')
    
    ax.set_theta_direction("clockwise")
    ax.set_theta_zero_location("N")
    
    # determine the buffer at the center of the plot
    # this is where ws <= `calm` and is evenly spread 
    # across all angles
    buffer = pct_calm / segments
    
    for i, (innerbar, outerbar) in enumerate(zip(rv.columns[:-1], rv.columns[1:])):
        if i == 0:
            # for the first bar, we need to plot the calm hole in the center first
            ax.bar(
                bar_midpoints,
                rv[innerbar].values,
                width=bar_width,
                bottom=buffer,
                label=innerbar,
                lw=lw,
                color=cp[i]
            )
            
        ax.bar(
            bar_midpoints,
            rv[outerbar].values,
            width=bar_width,
            label=outerbar,
            bottom=buffer + rv.cumsum(axis=1)[innerbar].values,
            lw=lw,
            color=cp[i+1]
        )
    
    if legend:
        ax.legend(
            loc="center left",
            handlelength=1, 
            handleheight=1,
            bbox_to_anchor=(1.1, 0, 0.5, 1)
        )
    
    if title:
        ax.set_title(title)
    
    # clean up the ticks and things
    ax.set_xticks([math.radians(x) for x in [0, 45, 90, 135, 180, 225, 270, 315]])
    ax.set_xticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])
    ax.set_yticklabels([])
    
    return ax