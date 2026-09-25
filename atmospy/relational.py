"""This file will contain regression figures."""

import warnings

import numpy as np
import seaborn as sns
from scipy.stats import linregress

from .utils import check_for_numeric_cols

__all__ = [
    "regplot",
]

# keyword arguments that would break the square, single-series layout of a
# regression plot, mapped to the reason they are rejected
_REJECTED_KWARGS = {
    "hue": "regplot draws a single series; facet with a seaborn FacetGrid to compare groups",
    "hue_order": "regplot draws a single series; facet with a seaborn FacetGrid to compare groups",
    "hue_norm": "regplot draws a single series; facet with a seaborn FacetGrid to compare groups",
    "kind": "regplot always draws a scatter joint plot",
    "dropna": "regplot always drops records with missing values",
    "xlim": "both axes share the same range; use `lim` to set it",
    "ylim": "both axes share the same range; use `lim` to set it",
}


def regplot(data, x, y, fit_reg=True, color=None, marker="o", lim=None, ylim=None, **kwargs):
    """Plot data and a best-fit line (OLS) between two variables.

    This figure is intended to convey the relationship between two variables. Often,
    this may be an air sensor and a reference sensor. It can also be two different
    variables where you are trying to understand the relationship. This function
    is a straight pass-through to Seaborn's `jointplot` with a few additions such
    as a unity line and explicitly listing the fit parameters of a linear model
    (Ordinary Least Squares).

    The plot is always square: both axes share the same range so that the
    unity line sits at 45 degrees and slope is read directly off the figure.

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
    lim : tuple of floats, optional
        The (min, max) range shared by both axes; if left as None,
        it is determined from the combined range of `x` and `y`, by default None
    ylim : tuple of floats, optional
        Deprecated alias for `lim`; will be removed in a future release.
    kwargs : dict or None, optional
        Additional keyword arguments are passed directly to the underlying
        :class:`seaborn.jointplot` call. Arguments that would break the
        square single-series layout (`hue`, `kind`, `xlim`, `ylim`, ...)
        raise a `TypeError`.

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

    Fix the range of both axes:

    >>> atmospy.regplot(df, x="Reference", y="Sensor A", lim=(0, 50))

    """
    check_for_numeric_cols(data, [x, y])

    # reject kwargs that would break the layout, naming the argument and the reason
    for name, reason in _REJECTED_KWARGS.items():
        if name in kwargs:
            raise TypeError(f"regplot() got an unsupported keyword argument {name!r}: {reason}.")

    # honor the deprecated alias for one release
    if ylim is not None:
        if lim is not None:
            raise TypeError("regplot() got both `lim` and the deprecated `ylim`; pass only `lim`.")

        warnings.warn(
            "The `ylim` argument of regplot is deprecated and will be removed in a "
            "future release; use `lim` instead.",
            FutureWarning, stacklevel=2,
        )
        lim = ylim

    # drop NaNs and keep only needed columns
    _data = data[[x, y]].dropna(how="any")

    xdata, ydata = _data[x], _data[y]

    # get the shared range for both axes
    if lim is None:
        lo = min([xdata.min(), ydata.min()])
        hi = max([xdata.max(), ydata.max()])
    else:
        lo, hi = lim

        if hi <= lo:
            raise ValueError("`lim` must be (min, max) with max larger than min.")

    # resolve the color once so the points, marginals, and fit line always agree
    if color is None:
        color = "C0"

    # make the call to jointplot
    g = sns.jointplot(
        data=_data,
        x=x,
        y=y,
        kind="scatter",
        color=color,
        marker=marker,
        xlim=(lo, hi),
        ylim=(lo, hi),
        **kwargs,
    )

    # add a unity line
    g.ax_joint.axline((0, 0), slope=1, ls="--", c="k", alpha=0.5, zorder=0, label="1:1")

    # if set, add a regression line
    if fit_reg:
        _x = np.linspace(lo, hi, 10)
        res = linregress(xdata, ydata)

        # build the label
        label = f"y = {res.slope:.2f}x"
        if res.intercept < 0:
            label += f" - {abs(res.intercept):.2f}"
        else:
            label += f" + {res.intercept:.2f}"

        # tack on the correlation coef.
        label += f"\n$r^2$ = {res.rvalue**2:.3f}"

        g.ax_joint.plot(_x, res.intercept + res.slope * _x, label=label, c=color)

    g.ax_joint.legend()

    return g
