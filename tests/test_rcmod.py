"""Test the theming helpers."""
import matplotlib as mpl
import pytest

from atmospy import set_theme


@pytest.fixture(autouse=True)
def _restore_rcparams():
    """Undo whatever set_theme did so rcParams never leak between tests."""
    with mpl.rc_context():
        yield


def test_set_theme_applies_atmospy_defaults():
    set_theme()

    assert mpl.rcParams["mathtext.default"] == "regular"
    # seaborn's "ticks" style keeps the spine ticks visible
    assert mpl.rcParams["xtick.bottom"] is True
    assert mpl.rcParams["ytick.left"] is True


def test_set_theme_merges_rc_overrides():
    set_theme(rc={"lines.linewidth": 7.5})

    assert mpl.rcParams["lines.linewidth"] == 7.5
    assert mpl.rcParams["mathtext.default"] == "regular"


def test_set_theme_rc_can_override_default():
    set_theme(rc={"mathtext.default": "it"})

    assert mpl.rcParams["mathtext.default"] == "it"
