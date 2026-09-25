"""Test the relational plots."""
import matplotlib as mpl
import numpy as np
import pytest
import seaborn as sns

from atmospy import regplot


def _legend_labels(g):
    return [t.get_text() for t in g.ax_joint.get_legend().get_texts()]


def _scatter_color(g):
    return g.ax_joint.collections[0].get_facecolor()[0][:3]


def _fit_line(g):
    return g.ax_joint.lines[-1]


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


def test_regplot_fit_label_matches_synthetic_slope(sensors):
    g = regplot(sensors, x="Reference", y="Sensor A")

    fit_label = next(label for label in _legend_labels(g) if label.startswith("y = "))
    slope = float(fit_label.split("x")[0].removeprefix("y = "))
    assert slope == pytest.approx(1.10, abs=0.05)


def test_regplot_is_square_by_default(sensors):
    g = regplot(sensors, x="Reference", y="Sensor A")

    assert g.ax_joint.get_xlim() == g.ax_joint.get_ylim()


def test_regplot_lim_sets_both_axes(sensors):
    g = regplot(sensors, x="Reference", y="Sensor A", lim=(0, 100))

    assert g.ax_joint.get_xlim() == (0, 100)
    assert g.ax_joint.get_ylim() == (0, 100)


def test_regplot_ylim_alias_warns_and_still_works(sensors):
    with pytest.warns(FutureWarning, match="`ylim`.*deprecated.*`lim`"):
        g = regplot(sensors, x="Reference", y="Sensor A", ylim=(0, 100))

    assert g.ax_joint.get_xlim() == (0, 100)
    assert g.ax_joint.get_ylim() == (0, 100)


def test_regplot_rejects_lim_and_ylim_together(sensors):
    with pytest.raises(TypeError, match="both `lim` and the deprecated `ylim`"):
        regplot(sensors, x="Reference", y="Sensor A", lim=(0, 100), ylim=(0, 100))


def test_regplot_rejects_inverted_lim(sensors):
    with pytest.raises(ValueError):
        regplot(sensors, x="Reference", y="Sensor A", lim=(10, 5))


@pytest.mark.parametrize("name, value", [
    ("hue", "Sensor B"),
    ("hue_order", ["a"]),
    ("hue_norm", (0, 1)),
    ("kind", "hex"),
    ("dropna", False),
    ("xlim", (0, 1)),
])
def test_regplot_rejects_layout_breaking_kwargs(sensors, name, value):
    with pytest.raises(TypeError, match=name):
        regplot(sensors, x="Reference", y="Sensor A", **{name: value})


def test_regplot_passes_other_kwargs_to_jointplot(sensors):
    g = regplot(sensors, x="Reference", y="Sensor A", marginal_kws={"bins": 5})

    # the top marginal histogram should have exactly five bars
    assert len(g.ax_marg_x.patches) == 5


def test_regplot_default_fit_line_matches_scatter_color(sensors):
    g = regplot(sensors, x="Reference", y="Sensor A")

    np.testing.assert_allclose(mpl.colors.to_rgb(_fit_line(g).get_color()), _scatter_color(g))


def test_regplot_custom_color_applies_to_points_and_fit(sensors):
    g = regplot(sensors, x="Reference", y="Sensor A", color="g")

    np.testing.assert_allclose(_scatter_color(g), mpl.colors.to_rgb("g"))
    assert mpl.colors.to_rgb(_fit_line(g).get_color()) == mpl.colors.to_rgb("g")


def test_regplot_requires_numeric_columns(sensors):
    df = sensors.assign(label="a")

    with pytest.raises(TypeError):
        regplot(df, x="Reference", y="label")
