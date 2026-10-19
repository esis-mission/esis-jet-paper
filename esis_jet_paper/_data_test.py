import astropy.time
import astropy.units as u
import numpy as np

import esis_jet_paper


def test_archive():
    directory = esis_jet_paper.archive()
    assert (directory / "complete").is_file()
    assert len(list((directory / "xrt").glob("*.fits"))) == 64
    assert len(list((directory / "aia").glob("*.fits"))) == 7 * 105
    assert len(list((directory / "hmi").glob("*.fits"))) == 28
    assert len(list((directory / "hmi_history").glob("*.fits"))) == 131
    assert len(list((directory / "iris").glob("*.fits.gz"))) == 1


def test_xrt():
    """Every Al_poly image from 18:00 to 18:20 UT, co-aligned with AIA, leak subtracted."""
    images = esis_jet_paper.xrt()
    time = images.inputs.time.ndarray
    assert time.size == 64
    assert np.all(time[1:] > time[:-1])
    assert time.min() >= astropy.time.Time("2019-09-30T18:00:00")
    assert time.max() < astropy.time.Time("2019-09-30T18:20:00")
    assert images.filter == "Al_poly"
    assert np.all(images.coalignment == 1)
    assert images.leak is not None
    assert np.all(images.leak == 0)
    assert images.uncertainty_map is not None


def test_aia():
    """The images of each channel are in order of time, and share one grid."""
    images = esis_jet_paper.aia()
    assert images.outputs.shape["time"] == 105
    assert images.outputs.shape["channel"] == 6
    wavelength = images.inputs.wavelength
    assert np.all(wavelength == esis_jet_paper.channels)
    time = images.inputs.time.ndarray
    assert np.all(time[1:] > time[:-1])
    position = images.inputs.position
    first = position[{"time": 0, "channel": 0}]
    assert np.all(np.abs(position.x - first.x) < 0.01 * u.arcsec)
    assert np.all(np.abs(position.y - first.y) < 0.01 * u.arcsec)


def test_aia_304():
    """The 304 angstrom images are in the same slots and on the same grid as the rest."""
    images = esis_jet_paper.aia_304()
    assert images.outputs.shape["time"] == 105
    assert images.outputs.shape["channel"] == 1
    assert np.all(images.inputs.wavelength == 304 * u.AA)
    time = images.inputs.time.ndarray
    assert np.all(time[1:] > time[:-1])
    position = images.inputs.position
    first = esis_jet_paper.aia().inputs.position[{"time": 0, "channel": 0}]
    assert np.all(np.abs(position.x - first.x) < 0.01 * u.arcsec)
    assert np.all(np.abs(position.y - first.y) < 0.01 * u.arcsec)


def test_hmi():
    """
    The 45 second magnetograms from 18:00:00 to 18:20:15 TAI are in order of
    time, in gauss, finite, and on the grid of AIA.
    """
    images = esis_jet_paper.hmi()
    assert images.outputs.shape == {"time": 28, "detector_y": 400, "detector_x": 400}
    assert images.outputs.unit == u.G
    assert np.all(np.isfinite(images.outputs))
    time = images.inputs.time.ndarray
    assert np.all(time[1:] > time[:-1])
    assert astropy.time.Time("2019-09-30T17:58") < time.min()
    assert time.max() < astropy.time.Time("2019-09-30T18:20")
    cadence = (time[1:] - time[:-1]).to(u.s)
    assert np.all(np.abs(cadence - 45 * u.s) < 1 * u.s)
    position = images.inputs.position
    first = esis_jet_paper.aia().inputs.position[{"time": 0, "channel": 0}]
    assert np.all(np.abs(position.x - first.x) < 0.01 * u.arcsec)
    assert np.all(np.abs(position.y - first.y) < 0.01 * u.arcsec)
