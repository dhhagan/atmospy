"""
Ozone by Year
=============

_thumb: .8, .8
"""
import atmospy
import pandas as pd
atmospy.set_theme()

# Load the example dataset
df = atmospy.load_dataset("us-ozone")

# Select a single location
single_site_ozone = df[
    df["Local Site Name"] == df["Local Site Name"].unique()[0]
]

atmospy.calendarplot(
    data=single_site_ozone, 
    x="Timestamp Local", 
    y="Sample Measurement", 
    freq="hour",
    xlabel="Day of Month",
    height=4,
    cmap="flare",
    vmin=0, vmax=80,
    title="Ozone in [Month]",
);