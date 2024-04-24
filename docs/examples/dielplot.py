"""
Diurnal Ozone
=============

_thumb: .4, .4
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

# Adjust the timestamp so that it is in local time
single_site_ozone["Timestamp Local"] = single_site_ozone["Timestamp GMT"].apply(
    lambda ts: ts + pd.Timedelta(hours=-7)
)

# Plot the diel trend
atmospy.dielplot(
    single_site_ozone,
    y="Sample Measurement", x="Timestamp Local",
    ylabel="$O_3 \; [ppm]$",
    plot_kws={"c": "g"}
)