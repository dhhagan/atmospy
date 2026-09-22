"""Test the pollution rose plot."""
import pytest

from atmospy import pollutionroseplot


def test_pollutionroseplot_basics(hourly):
    calm = 0.5
    ax = pollutionroseplot(
        data=hourly, ws="ws", wd="wd", pollutant="pm25",
        bins=[0, 10, 20, 40], segments=12, calm=calm,
    )

    assert ax.name == "polar"

    # three closed bins plus the open-ended catch-all, one stacked bar per segment
    assert len(ax.containers) == 4
    assert all(len(container) == 12 for container in ax.containers)

    # the stacked bars account for exactly the non-calm fraction of the data
    total = sum(sum(bar.get_height() for bar in c) for c in ax.containers)
    assert total == pytest.approx(100.0 * (hourly["ws"] > calm).mean())


def test_pollutionroseplot_labels_and_legend(hourly):
    ax = pollutionroseplot(
        data=hourly, ws="ws", wd="wd", pollutant="pm25",
        bins=[0, 10, 20], suffix="ppb", title="rose",
    )

    labels = [t.get_text() for t in ax.get_legend().get_texts()]
    assert labels == ["0 to 10 ppb", "10 to 20 ppb", ">20 ppb"]
    assert ax.get_title() == "rose"
    assert [t.get_text() for t in ax.get_xticklabels()] == ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def test_pollutionroseplot_no_legend(hourly):
    ax = pollutionroseplot(data=hourly, ws="ws", wd="wd", pollutant="pm25", bins=[0, 10], legend=False)

    assert ax.get_legend() is None


def test_pollutionroseplot_requires_numeric_columns(hourly):
    with pytest.raises(TypeError):
        pollutionroseplot(data=hourly, ws="ws", wd="timestamp", pollutant="pm25")
