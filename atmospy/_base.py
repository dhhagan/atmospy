"""Internal helpers shared across the plotting modules."""

import matplotlib as mpl
import numpy as np


def _colorbar_extend(im, values):
    """Pick the colorbar `extend` mode from where `values` fall relative to the color limits."""
    values = np.asarray(np.ma.filled(values, np.nan), dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return "neither"

    vmin, vmax = im.get_clim()
    below = values.min() < vmin
    above = values.max() > vmax

    if below and above:
        return "both"
    if above:
        return "max"
    if below:
        return "min"
    return "neither"


def _add_colorbar(im, ax, cbar_kws=None, units=None, values=None, **defaults):
    """Attach a colorbar for `im` to `ax` without mutating the caller's `cbar_kws`.

    If `values` (the data behind `im`) is given, the colorbar grows a pointed
    cap on whichever end has values clipped by the color limits, unless the
    caller set `extend` themselves.
    """
    kws = dict(defaults, **(cbar_kws or {}))

    if values is not None and "extend" not in kws:
        kws["extend"] = _colorbar_extend(im, values)

    cb = ax.figure.colorbar(im, ax=ax, **kws)
    cb.outline.set_visible(False)

    # keep the colorbar uncluttered regardless of orientation
    cb.locator = mpl.ticker.MaxNLocator(4)
    cb.update_ticks()

    if units:
        cb.set_label(units)

    return cb
