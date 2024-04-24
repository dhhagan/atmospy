"""This file contains the wind and pollution rose figures."""
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from .utils import (
    check_for_numeric_cols,
)

__all__ = ["pollutionroseplot"]

def pollutionroseplot(data=None, *, ws=None, wd=None, pollutant=None, 
                      faceted=False, segments=12, bins=[0, 10, 100, 1000], suffix="a.u.",
                      calm=0., lw=1, legend=True, palette="flare",
                      title=None, **kwargs):
    """_summary_


    The basis of this function can orginally found here: https://gist.github.com/phobson/41b41bdd157a2bcf6e14
    
    Parameters
    ----------
    data : _type_, optional
        _description_, by default None
    ws : _type_, optional
        _description_, by default None
    wd : _type_, optional
        _description_, by default None
    pollutant : _type_, optional
        _description_, by default None
    faceted : bool, optional
        _description_, by default False
    segments : int, optional
        _description_, by default 12
    bins : list, optional
        _description_, by default [0, 10, 100, 1000]
    suffix : str, optional
        _description_, by default "a.u."
    calm : _type_, optional
        _description_, by default 0.
    lw : int, optional
        _description_, by default 1
    legend : bool, optional
        _description_, by default True
    palette : str, optional
        _description_, by default "flare"
    title : _type_, optional
        _description_, by default None
    """
    check_for_numeric_cols(data, [ws, wd, pollutant])

    # if the bins don't end in inf, add it
    if not np.isinf(bins[-1]):
        bins.append(np.inf)
        
    # 
    bins = np.asarray(bins)
    
    # setup the color palette
    cp = sns.color_palette(palette, n_colors=bins.shape[0])
    
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
        thetas = (thetas[:-1] + thetas[1:])/2.
        
        midpoints = [math.radians(theta) for theta in (thetas*np.pi/180. - np.pi/thetas.shape[0])]
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
        .applymap(lambda x: 100 * data.shape[0])
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