import astropy.units as u

import esis_jet_paper


def test_points():
    """
    Every point has a radius and a line style, and the base and the footpoint
    share one radius, which the captions cite as one number.
    """
    points = esis_jet_paper.points
    assert set(esis_jet_paper.radii) == set(points)
    assert set(esis_jet_paper.linestyles) == set(points)
    assert esis_jet_paper.radii["base"] == esis_jet_paper.radii["footpoint"]


def test_length():
    """
    The length of event E is the angle from its base to its northern
    footpoint at about 0.73 Mm per arcsecond, as seen from about 1 AU.
    """
    (x_base, y_base), (x_footpoint, y_footpoint) = (
        esis_jet_paper.points["base"],
        esis_jet_paper.points["footpoint"],
    )
    angle = ((x_footpoint - x_base) ** 2 + (y_footpoint - y_base) ** 2) ** 0.5
    scale = esis_jet_paper._points.length() / (angle * u.arcsec)
    assert 0.72 * u.Mm / u.arcsec < scale < 0.73 * u.Mm / u.arcsec
