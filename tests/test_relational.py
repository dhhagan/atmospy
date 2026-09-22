"""Test the relational plots."""
import pytest
import seaborn as sns

from atmospy import regplot


def _legend_labels(g):
    return [t.get_text() for t in g.ax_joint.get_legend().get_texts()]


def test_regplot_returns_jointgrid_with_fit(sensors):
    g = regplot(sensors, x="Reference", y="Sensor A")

    assert isinstance(g, sns.JointGrid)

    labels = _legend_labels(g)
    assert "1:1" in labels
    assert any(label.startswith("y = ") for label in labels)


def test_regplot_without_fit(sensors):
    g = regplot(sensors, x="Reference", y="Sensor A", fit_reg=False)

    labels = _legend_labels(g)
    assert "1:1" in labels
    assert not any(label.startswith("y = ") for label in labels)


def test_regplot_square_axes_from_data(sensors):
    g = regplot(sensors, x="Reference", y="Sensor A")

    assert g.ax_joint.get_xlim() == g.ax_joint.get_ylim()


def test_regplot_explicit_ylim(sensors):
    g = regplot(sensors, x="Reference", y="Sensor A", ylim=(0, 100))

    assert g.ax_joint.get_xlim() == (0, 100)
    assert g.ax_joint.get_ylim() == (0, 100)


def test_regplot_rejects_inverted_ylim(sensors):
    with pytest.raises(ValueError):
        regplot(sensors, x="Reference", y="Sensor A", ylim=(10, 5))


def test_regplot_requires_numeric_columns(sensors):
    df = sensors.assign(label="a")

    with pytest.raises(TypeError):
        regplot(df, x="Reference", y="label")
