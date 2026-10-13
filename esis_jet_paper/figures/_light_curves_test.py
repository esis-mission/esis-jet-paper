import aastex
import astropy.time
import numpy as np

import esis_jet_paper


def test_light_curves():
    """The figure has a line for every channel of AIA and for XRT."""
    figure = esis_jet_paper.figures.light_curves()
    assert isinstance(figure, aastex.Figure)
    assert figure.animation is None
    channels = esis_jet_paper.figures._light_curves._channels()
    assert len(channels) == 8
    colors = [color for _, color, _, _, _ in channels]
    colors.append(esis_jet_paper.color_esis)
    assert len(set(colors)) == len(colors)


def test_peak():
    """
    The base of event E peaks within a few minutes of 18:08 UT in every
    channel, well above the median of the image.
    """
    channels = esis_jet_paper.figures._light_curves._channels()
    for title, _, time, curves, median in channels:
        base = curves["base"]
        index = np.nanargmax(base.ndarray)
        peak = astropy.time.Time(time.ndarray[index])
        assert astropy.time.Time("2019-09-30T18:06") < peak, title
        assert peak < astropy.time.Time("2019-09-30T18:11"), title
        assert base[{"time": index}] > 3 * median[{"time": index}], title


def test_saturated():
    """The base is left out of exactly the XRT images in which it saturated."""
    _, _, _, curves, _ = esis_jet_paper.figures._light_curves._channels()[-1]
    images = esis_jet_paper.xrt()
    center = images.inputs.position.cell_centers(axis=("detector_x", "detector_y"))
    x, y = esis_jet_paper.points["base"]
    radius = esis_jet_paper.figures._light_curves.radius
    distance = np.sqrt(
        np.square(center.x - x * radius.unit) + np.square(center.y - y * radius.unit)
    )
    saturated = np.any(
        (distance <= radius) & images.saturated,
        axis=("detector_x", "detector_y"),
    )
    assert np.any(saturated)
    assert np.all(np.isnan(curves["base"]) == saturated)
