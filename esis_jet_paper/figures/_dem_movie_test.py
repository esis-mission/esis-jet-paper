import aastex

import esis_jet_paper


def test_dem_movie():
    """
    The figure carries its movie, which is small enough for the AAS journals
    and is linked from the caption.
    """
    figure = esis_jet_paper.figures.dem_movie()
    assert isinstance(figure, aastex.Figure)
    animation = figure.animation
    assert animation is not None
    assert animation.source.is_file()
    assert animation.source.stat().st_size < 15e6
    assert animation.url == esis_jet_paper.url("dem-event-e.mp4")
    assert "watched at" in figure.dumps()
