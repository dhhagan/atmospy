import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from .utils import (
    remove_na,
)
from .utils import (
    check_for_numeric_cols,
    check_for_timestamp_col
)

__all__ = ["dielplot", ]


def dielplot(data, x, y, 
             ax=None, ylim=None, xlabel=None, ylabel=None, title=None,
             plot_kws=None, **kwargs
             ):
    """_summary_

    Parameters
    ----------
    data : _type_
        _description_
    x : _type_
        _description_
    y : _type_
        _description_
    ax : _type_, optional
        _description_, by default None
    ylim : _type_, optional
        _description_, by default None
    xlabel : _type_, optional
        _description_, by default None
    ylabel : _type_, optional
        _description_, by default None
    title : _type_, optional
        _description_, by default None
    plot_kws : _type_, optional
        _description_, by default None
    """
    default_plot_kws = {
        "lw": 3,
    }
    
    # complete some initial data quality checks
    check_for_timestamp_col(data, x)
    check_for_numeric_cols(data, [y])
    
    # 
    plot_kws = {} if plot_kws is None else dict(default_plot_kws, **plot_kws)
    
    # copy over only the needed data
    _data = data[[x, y]].copy(deep=True)
    _data = _data.set_index(x)
    
    # 
    # figure setup
    if ax is None:
        ax = plt.gca()
        
    # compute the diel statistics
    stats = _data.groupby([_data.index.hour, _data.index.minute], as_index=False).describe()
    
    # build an index we can use to make the figure
    index = stats.index.values
    freq = int(60 / (index.size / 24))
    figure_index = pd.date_range(start='2020-01-01', periods=index.size, freq=f"{freq}min")
    
    # plot the diel average
    ax.plot(figure_index, stats[y]['mean'], **plot_kws)
    
    # add the IQR as a shaded region
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