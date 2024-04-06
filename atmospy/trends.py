from .utils import (
    remove_na,
)
from seaborn import (
    FacetGrid,
)

__all__ = ["dielplot", ]


def dielplot():
    """_summary_
    Diurnal on a strictly 24-h basis. Should be 
      - able to be continuous with or without err bars
      - able to be a box plot with/wo whiskers
      - properly labeled
      - should assume a timeseries and do the math
    """
    return