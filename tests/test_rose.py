"""Test the relational plots."""
import pytest
from atmospy import pollutionroseplot
import pandas as pd
import matplotlib as mpl
from atmospy import load_dataset
import seaborn as sns

def test_scatter_basics():
    df = load_dataset("air-sensors-met")
    
    ax = pollutionroseplot(
        data=df, ws="ws", wd='wd', pollutant="pm1", suffix="ppb", 
        segments=30, calm=0.1
    )
    
    assert isinstance(ax, mpl.axes._axes.Axes)