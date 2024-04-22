"""Test the relational plots."""
import pytest
from atmospy import regplot
import pandas as pd
import matplotlib as mpl
from atmospy import load_dataset
import seaborn as sns

def test_scatter_basics():
    df = load_dataset("air-sensors-pm")
    
    ax = regplot(
        df, x="Reference", y='Sensor A',
    )
    
    assert isinstance(ax, sns.axisgrid.JointGrid)