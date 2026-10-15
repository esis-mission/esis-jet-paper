import aastex
import astropy.units as u
import numpy as np

import esis_jet_paper

_axis = ("detector_x", "detector_y")


def test_backgrounds():
    """The figure is a still, with no movie."""
    figure = esis_jet_paper.figures.backgrounds()
    assert isinstance(figure, aastex.Figure)
    assert figure.animation is None


def test_still():
    """
    Both backgrounds are finite everywhere, and the wider is the smoother in
    every channel. Under the base of event E, either is a small part of the
    intensity in every channel, and under the spire most of it, as the
    appendix says.
    """
    module = esis_jet_paper.figures._backgrounds
    observation, background = module._still()
    assert list(background) == [esis_jet_paper._dem._size_background, module.size_wide]

    index = module._nearest(observation)
    for size, intensity in background.items():
        assert np.all(np.isfinite(intensity)), size
        fraction = (intensity / observation.intensity).to(u.dimensionless_unscaled)
        assert np.all(fraction[index["base"]] < 0.3), size
        assert np.all(fraction[index["spire"]] > 0.5), size

    narrow, wide = background.values()
    assert np.all(np.std(wide, axis=_axis) < np.std(narrow, axis=_axis))
