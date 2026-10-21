import aastex
import astropy.time
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np

import esis_jet_paper

_module = esis_jet_paper.figures._time_series


def test_time_series():
    """
    The figure carries its movie, which is small enough for the AAS journals
    and is linked from the caption.
    """
    figure = esis_jet_paper.figures.time_series()
    assert isinstance(figure, aastex.Figure)
    animation = figure.animation
    assert animation is not None
    assert animation.source.is_file()
    assert animation.source.stat().st_size < 15e6
    assert animation.url == esis_jet_paper.url("time-series-event-e.mp4")
    assert "watched online" in figure.dumps()


def test_frames():
    """One frame for each image of AIA 304 Å from 18:00 to 18:20 UT, 12 s apart."""
    frames = _module.frames()
    assert frames.size == 105
    assert astropy.time.Time("2019-09-30T17:59:30") < frames[0]
    assert frames[-1] < astropy.time.Time("2019-09-30T18:21")
    step = (frames[1:] - frames[:-1]).to(u.s)
    assert np.all(np.abs(step - 12 * u.s) < 1 * u.s)


def test_index_still():
    """
    The still is the frame closest to the still of the DEM movie, during the
    exposures of ESIS.
    """
    time = _module.frames()[_module.index_still()]
    time_still = esis_jet_paper.figures._dem_movie.time_still
    assert np.abs((time - time_still).to(u.s)) <= 6 * u.s
    start, stop = _module.exposures_esis
    assert start < time < stop


def test_panels():
    """
    In every frame from the first image of an instrument to its last, its
    panel shows the image whose exposure is centered closest to the frame,
    at most half of the longest gap between its images away.
    """
    frames = _module.frames()
    for panel in _module._panels():
        gap = np.max((panel.time[1:] - panel.time[:-1]).to(u.s))
        for frame in frames:
            if not (panel.time[0] <= frame <= panel.time[-1]):
                continue
            offset = (panel.time[panel.index(frame)] - frame).to(u.s)
            assert np.abs(offset) <= gap / 2


def test_panels_field():
    """
    The pixels kept in every image of every panel cover the field of the DEM
    movie, and the colors of each span its intensities.
    """
    (x_min, x_max), (y_min, y_max) = esis_jet_paper.figures._dem_movie._field()
    axis = ("detector_x", "detector_y")
    for panel in _module._panels():
        x = panel.position.x
        y = panel.position.y
        assert np.all(x.min(axis=axis) <= x_min * u.arcsec)
        assert np.all(x.max(axis=axis) >= x_max * u.arcsec)
        assert np.all(y.min(axis=axis) <= y_min * u.arcsec)
        assert np.all(y.max(axis=axis) >= y_max * u.arcsec)
        assert panel.norm.vmin < panel.norm.vmax


def test_draw_esis():
    """
    The panel of ESIS says its images are to come during its exposures, and
    that there are none outside of them.
    """
    fig, ax = plt.subplots()
    _module._draw_esis(ax, astropy.time.Time("2019-09-30T18:08:00"))
    assert [text.get_text() for text in ax.texts] == ["to come"]
    _module._draw_esis(ax, astropy.time.Time("2019-09-30T18:02:00"))
    assert [text.get_text() for text in ax.texts] == ["no exposure"]
    plt.close(fig)
