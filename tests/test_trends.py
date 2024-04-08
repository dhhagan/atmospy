"""Test the trend plots."""
import pytest
from atmospy import dielplot
import pandas as pd
import matplotlib as mpl
from atmospy import load_dataset

def prep_diel_dataset(rs='1min'):
    df = load_dataset("us-ozone")
    
    single_site_ozone = df[df['Local Site Name'] == df['Local Site Name'].unique()[0]]
    
    # Adjust the timezone
    single_site_ozone.loc[:, 'Timestamp Local'] = single_site_ozone['Timestamp GMT'].apply(lambda x: x + pd.Timedelta(hours=-7))
    
    # Resample to {rs}min
    single_site_ozone = single_site_ozone.set_index("Timestamp Local").resample(rs).interpolate('linear').reset_index()
    
    # Adjust to ppb
    single_site_ozone['Sample Measurement'] *= 1e3
    
    return single_site_ozone

def test_dielplot_basics():
    df = prep_diel_dataset('15min')
    
    ax = dielplot(
        df, x="Timestamp Local", y='Sample Measurement',
    )
    
    assert isinstance(ax, mpl.axes._axes.Axes)