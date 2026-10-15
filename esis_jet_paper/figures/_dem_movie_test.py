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
    assert "watched online" in figure.dumps()


def test_field():
    """
    The field that every frame fills holds the base of event E, at about
    (49, -86) arcsec, its spire, at about (52, -51) arcsec, and its northern
    footpoint, at about (68, 0) arcsec, with room to spare.
    """
    xlim, ylim = esis_jet_paper.figures._dem_movie._field()
    for x, y in [(49, -86), (52, -51), (68, 0)]:
        assert xlim[0] + 15 < x < xlim[1] - 15
        assert ylim[0] + 15 < y < ylim[1] - 15
