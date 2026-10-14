import aastex
import astropy.units as u
import numpy as np

import esis_jet_paper


def test_dem_regions():
    """The figure is a still, with no movie."""
    figure = esis_jet_paper.figures.dem_regions()
    assert isinstance(figure, aastex.Figure)
    assert figure.animation is None


def test_inversions():
    """
    In every region, the DEM from AIA alone predicts more XRT intensity than
    is observed, and the DEM from AIA and XRT predicts it to within 10%.
    """
    regions = esis_jet_paper.figures._dem_regions.inversions()
    assert list(regions) == list(esis_jet_paper.points) + ["background"]
    for name, region in regions.items():
        assert region.ratio_aia > 1, name
        assert abs(region.ratio - 1) < 0.1, name


def test_background():
    """
    The background region lies inside the field of the DEM, and well away
    from every point of event E.
    """
    module = esis_jet_paper.figures._dem_regions
    x, y = module.background
    radius = module.radius_background.to_value(u.arcsec)
    xlim, ylim = esis_jet_paper.figures._dem_movie._field()
    assert xlim[0] + radius < x < xlim[1] - radius
    assert ylim[0] + radius < y < ylim[1] - radius
    for name, (x_point, y_point) in esis_jet_paper.points.items():
        assert np.hypot(x - x_point, y - y_point) > 20, name
