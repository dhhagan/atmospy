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

__all__ = ["calendarplot", ]


def calendarplot():
  """Calendar plot with func for faceting by week, month, year, etc"""
  return