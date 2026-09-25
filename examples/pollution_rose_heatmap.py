"""
Mean PM2.5 by Wind Direction and Speed
======================================

_thumb: .8, .8
"""
import atmospy
atmospy.set_theme()

# Load the example dataset
df = atmospy.load_dataset("air-sensors-met")

# Cut the data by wind direction and wind speed, and color each cell
# by the mean PM2.5 in that cell. High values at low wind speed point
# to a nearby source; high values at high speed point to transport.
atmospy.pollutionroseplot(
    data=df, wd="wd", ws="ws", pollutant="pm25",
    kind="heatmap", segments=16, calm=0.1, min_count=10,
    suffix="$µgm^{-3}$",
)
