"""This file will contain regression figures.
"""
from .utils import (
    remove_na,
)
from seaborn import (
    FacetGrid,
)

__all__ = ["regplot", ]

def regplot():
    """Standard regression plot between two variables.
    """