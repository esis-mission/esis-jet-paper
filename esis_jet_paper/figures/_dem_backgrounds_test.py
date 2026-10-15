import aastex
import astropy.units as u
import numpy as np

import esis_jet_paper


def test_dem_backgrounds():
    """The figure is a still, with no movie."""
    figure = esis_jet_paper.figures.dem_backgrounds()
    assert isinstance(figure, aastex.Figure)
    assert figure.animation is None


def test_inversions():
    """
    The DEM of either background fits it to within its noise, on the median,
    and under the spire holds most of the emission measure of the spire itself,
    as the appendix says.
    """
    module = esis_jet_paper.figures._backgrounds
    observation, _ = module._still()
    spire = module._nearest(observation)["spire"]
    index = esis_jet_paper.figures._dem_movie.index_still()
    observed = esis_jet_paper.dem().dem.outputs[{"time": index}][spire]
    inversions = esis_jet_paper.figures._dem_backgrounds.inversions()
    assert list(inversions) == [esis_jet_paper._dem._size_background, module.size_wide]
    for size, (dem, chi2) in inversions.items():
        assert dem.outputs.shape == observed.shape | chi2.shape, size
        assert 0.8 < float(np.median(chi2).ndarray) < 1.2, size
        ratio = (dem.outputs[spire].sum() / observed.sum()).to(u.dimensionless_unscaled)
        assert float(ratio.ndarray) > 0.5, size
