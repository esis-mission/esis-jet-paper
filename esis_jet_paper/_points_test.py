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
