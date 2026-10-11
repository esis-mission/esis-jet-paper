import numpy as np

import esis_jet_paper


def test_dem():
    """
    There is a DEM for every XRT image and every pixel where XRT did not
    saturate, which fits the seven channels to within their noise.
    """
    inversion = esis_jet_paper.dem()

    assert inversion.time.size == 64
    shape = {"time": 64, "detector_x": 128, "detector_y": 128}
    assert inversion.chi2.shape == shape
    assert inversion.saturated.shape == shape
    assert inversion.dem.outputs.shape == shape | {"temperature": 51}

    missing = np.isnan(inversion.dem.outputs).any("temperature")
    assert np.all(missing == inversion.saturated)
    assert np.all((inversion.chi2 < 0) == inversion.saturated)

    num_saturated = inversion.saturated.sum(("detector_x", "detector_y"))
    assert np.count_nonzero(num_saturated.ndarray) == 2

    # the few saturated pixels, whose chi squared is -1, barely move the median
    assert 0.8 < inversion.chi2.median().ndarray < 1.2
    assert 0 < inversion.ratio_noise < 1
