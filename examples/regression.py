"""
Regression Plot
===============

_thumb: .4, .4
"""
import atmospy
atmospy.set_theme()

# Load the example dataset
df = atmospy.load_dataset("air-sensors-pm")

# Plot a pollution rose example for PM2.5
atmospy.regplot(
    df, x="Reference", y="Sensor A",
    ylim=(0, 60),
    color="g",
    # title="Performance of Sensor A vs US EPA FEM Reference"
)