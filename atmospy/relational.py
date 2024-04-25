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
    """Plot data and a best-fit line (OLS) between two variables.
    
    This figure is intended to convey the relationship between two variables. Often,
    this may be an air sensor and a reference sensor. It can also be two different 
    variables where you are trying to understand the relationship. This function 
    is a straight pass-through to Seaborn's `jointplot` with a few additions such 
    as a unity line and explicitly listing the fit parameters of a linear model 
    (Ordinary Least Squares).
    
    Since it is directly passed through to Seaborn's `jointplot`, it is incredibly 
    customizable and powerful. Please see the Seaborn docs for more details.

    Parameters
    ----------
    data : :class:`pandas.DataFrame`
        Tabular data as a pandas DataFrame. This should be a wide-form dataset 
        where the x and y keys are columns in the DataFrame.
    x : key in `data`
        Variable that corresponds to the data plotted on the x axis.
    y : key in `data`.
        Variable that corresponds to the data plotted on the y axis.
    fit_reg : bool, optional
        If `True`, a linear regression model will be fit to the data 
        and fit parameters listed in the legend, by default True
    color : str, optional
        A single color to map to the data; if None, the next 
        color in the color cycle will be used, by default None
    marker : str, optional
        A single marker style to use to plot the data, by default "o"
    ylim : tuple of floats, optional
        Set the limits of the figure on both axes using the 
        ylim (the plot is forced to be squared); if left as None, 
        defaults will be determined from the underlying data, by default None
    kwargs : dict or None, optional
        Additional keyword arguments are passed directly to the underlying 
        :class:`seaborn.jointplot` call.
        
    Returns
    -------
    :class:`seaborn.JointGrid`
        An object with multiple subplots including the 
        joint (primary) and marginal (top and right) axes.
        
        
    Examples
    --------
    Using defaults, plot the relationship between a reference particle monitor 
    and an air sensor:
    
    >>> df = atmospy.load_dataset("air-sensors-pm")
    >>> atmospy.regplot(df, x="Reference", y="Sensor A")
    
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
        label = f"y = {res.slope:.2f}x"
        if res.intercept < 0:
            label += f" - {res.intercept:.2f}"
        else:
            label += f" + {res.intercept:.2f}"
        
        # tack on the correlation coef.
        label += f"\n$r^2$ = {res.rvalue**2:.3f}"
        
        g.ax_joint.plot(_x, res.intercept + res.slope*_x, label=label, c=color)
    
    g.ax_joint.legend()
    
    return g