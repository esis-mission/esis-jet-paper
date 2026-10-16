import aastex
import astropy.units as u
import numpy as np

import esis_jet_paper


def test_flux_history():
    """The figure is a still, with no movie."""
    figure = esis_jet_paper.figures.flux_history()
    assert isinstance(figure, aastex.Figure)
    assert figure.animation is None


def test_noise():
    """The noise of every magnetogram is a few gauss."""
    noise = esis_jet_paper.figures._flux_history.noise()
    assert noise.shape == {"time": 131}
    assert np.all(noise > 2 * u.G)
    assert np.all(noise < 5 * u.G)


def test_centers():
    """
    Each circle is within an arcsecond of its point in the magnetogram closest
    to the still, and a day before, about 220 arcseconds further east.
    """
    module = esis_jet_paper.figures._flux_history
    index = module.index_still()
    for name, center in module._centers().items():
        x, y = esis_jet_paper.points[name]
        still = center[{"time": index}]
        assert np.abs(still.x - x * u.arcsec) < 1 * u.arcsec, name
        assert np.abs(still.y - y * u.arcsec) < 1 * u.arcsec, name
        first = center[{"time": 0}]
        assert 200 * u.arcsec < still.x - first.x < 240 * u.arcsec, name


def test_history():
    """
    The base sits in negative polarity, with much less positive flux beside it,
    while the positive flux at the northern footpoint grows to a peak during
    the day and falls again before event E.
    """
    history = esis_jet_paper.figures._flux_history.history()
    for name, polarities in history.items():
        for polarity, flux in polarities.items():
            assert flux.shape == {"time": 131}, (name, polarity)
            assert np.all(flux >= 0 * u.Mx), (name, polarity)

    base = history["base"]
    assert np.all(base["negative"] > 2 * base["positive"])

    footpoint = history["footpoint"]["positive"]
    peak = np.max(footpoint, axis="time")
    assert peak > 2 * footpoint[{"time": 0}]
    assert peak > 2 * footpoint[{"time": -1}]
