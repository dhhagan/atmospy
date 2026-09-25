"""Test the (not yet implemented) distribution plots."""
import pytest

from atmospy.distributions import bananaplot, psdplot


def test_psdplot_not_implemented():
    with pytest.raises(NotImplementedError):
        psdplot()


def test_bananaplot_not_implemented():
    with pytest.raises(NotImplementedError):
        bananaplot()
