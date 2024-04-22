"""This file will contain regression figures.
"""
import seaborn as sns
import numpy as np
from scipy.stats import (
    linregress,
)
from .utils import (
    remove_na,
    check_for_numeric_cols
)

__all__ = ["regplot", ]

def regplot(data, x, y, fit_reg=True, color=None, marker="o", ylim=None, **kwargs):
    """Plot data and a linear regression best fit line between the two variables.
    
    This function builds on Seaborn's `jointplot` and most kwargs can be passed 
    straight through to the `jointplot` for customization.

    Parameters
    ----------
    data : pd.DataFrame
        Input data structure.
    x : str
        Variable that corresponds to the x data in `data`.
    y : str
        _description_
    fit_reg : bool, optional
        _description_, by default True
    color : _type_, optional
        _description_, by default None
    marker : str, optional
        _description_, by default "o"
    ylim : _type_, optional
        _description_, by default None
    """
    check_for_numeric_cols(data, [x, y])
    
    # drop NaNs and keep only needed columns
    _data = data[[x, y]].dropna(how='any')
    
    xdata, ydata = _data[x], _data[y]
    
    # get the range for the plot
    if ylim is None:
        ymin = min([xdata.min(), ydata.min()])
        ymax = max([xdata.max(), ydata.max()])
    else:
        ymin = ylim[0]
        ymax = ylim[1]
        
        if ymax <= ymin:
            raise ValueError("`ymax` must be larger than `ymin`")
    
    # update the kwargs
    kwargs.update({"color": color, "marker": marker})
    
    # remove certain kwargs that we don't want to allow to be passed to the jointplot
    for each in (
        "hue",
        "kind",
        "dropna",
        "xlim",
        "ylim",
        "hue_order",
        "hue_norm"
    ):
        if each in kwargs:
            kwargs.pop(each)
            
    # set the color if one wasn't explicitly set
    if color is None:
        color = "C0"
    
    # make the call to jointplot
    g = sns.jointplot(
        data=_data, x=x, y=y, kind="scatter",
        xlim=(ymin, ymax),
        ylim=(ymin, ymax),
        **kwargs
    )
    
    # add a unity line
    g.ax_joint.axline(
        (0, 0), slope=1, ls='--',
        c='k', alpha=0.5, zorder=0, label="1:1"
    )
    
    # if set, add a regression line
    if fit_reg:
        _x = np.linspace(ymin, ymax, 10)
        res = linregress(xdata, ydata)
        
        # build the label
        label = f"y = {res.slope:.2f}"
        if res.intercept < 0:
            label += f" - {res.intercept:.2f}"
        else:
            label += f" + {res.intercept:.2f}"
        
        # tack on the correlation coef.
        label += f"\n$r^2$ = {res.rvalue**2:.3f}"
        
        g.ax_joint.plot(_x, res.intercept + res.slope*_x, label=label, c=color)
    
    g.ax_joint.legend()
    
    return g