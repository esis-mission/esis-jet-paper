import dataclasses
import pathlib

import astropy.io.fits
import astropy.time
import astropy.units as u
import named_arrays as na
import numpy as np
import pytest
import sdo

import esis_jet_paper


def _flat(tmp_path: pathlib.Path, num: int, value: float) -> sdo.aia.Filtergram:
    """
    An AIA image of `num` by `num` pixels of 0.6 arcseconds centered on
    (100, 200) arcseconds, all equal to `value`.
    """
    header = astropy.io.fits.Header()
    header["CTYPE1"] = "HPLN-TAN"
    header["CTYPE2"] = "HPLT-TAN"
    header["CUNIT1"] = "arcsec"
    header["CUNIT2"] = "arcsec"
    header["CRPIX1"] = (num + 1) / 2
    header["CRPIX2"] = (num + 1) / 2
    header["CRVAL1"] = 100.0
    header["CRVAL2"] = 200.0
    header["CDELT1"] = 0.6
    header["CDELT2"] = 0.6
    header["DATE-OBS"] = "2024-05-10T17:59:47"
    header["MJD-OBS"] = astropy.time.Time(header["DATE-OBS"]).mjd
    header["EXPTIME"] = 2.0
    path = tmp_path / "a.fits"
    data = np.full((num, num), value, dtype=float)
    astropy.io.fits.PrimaryHDU(data, header).writeto(path)
    return sdo.aia.Filtergram.from_fits(path=path, wavelength=171 * u.AA)


def _grid(num: int, pitch: u.Quantity) -> na.Cartesian2dVectorArray:
    """The vertices of `num` by `num` pixels centered on the images of `_flat`."""
    center = na.Cartesian2dVectorArray(100, 200) * u.arcsec
    edge = (num / 2) * pitch
    return center + na.Cartesian2dVectorArray(
        x=na.linspace(-edge, edge, axis="x", num=num + 1),
        y=na.linspace(-edge, edge, axis="y", num=num + 1),
    )


@pytest.mark.parametrize("fwhm", [1.3 * u.arcsec, 2 * u.arcsec])
def test_resample_flat(tmp_path: pathlib.Path, fwhm: u.Quantity) -> None:
    """
    A flat image stays flat, with the signal of each new pixel its area in
    AIA pixels times the signal of one, blurred or not.
    """
    images = _flat(tmp_path, num=40, value=3)
    pitch = 1.1 * u.arcsec
    counts, uncertainty, _ = esis_jet_paper._dem._resample(
        images=images,
        uncertainty=1 * u.DN,
        position=_grid(12, pitch),
        axis=("x", "y"),
        fwhm=fwhm,
    )
    area = float(np.square(pitch / (0.6 * u.arcsec)))
    assert counts.shape == {"y": 12, "x": 12}
    assert np.allclose(counts.ndarray, 3 * area * u.DN, rtol=1e-6)
    assert np.all(uncertainty < np.sqrt(area) * u.DN)


def test_resample_conserves(tmp_path: pathlib.Path) -> None:
    """
    Without a blur, the signal of new pixels which cover the image is all
    the signal of the image.
    """
    images = _flat(tmp_path, num=8, value=1)
    rng = np.random.default_rng(0)
    outputs = na.ScalarArray(rng.uniform(size=(8, 8)), images.outputs.axes) * u.DN
    images = dataclasses.replace(images, outputs=outputs)
    counts, _, _ = esis_jet_paper._dem._resample(
        images=images,
        uncertainty=1 * u.DN,
        position=_grid(5, 1.5 * u.arcsec),
        axis=("x", "y"),
        fwhm=1.3 * u.arcsec,
    )
    assert np.isclose(counts.sum().ndarray, images.outputs.sum().ndarray)


def test_resample_noise(tmp_path: pathlib.Path) -> None:
    """
    The uncertainty matches the scatter of the new pixels when the images
    are noisy with that uncertainty, on average over the pixels.
    """
    images = _flat(tmp_path, num=40, value=0)
    kwargs = {
        "uncertainty": 2 * u.DN,
        "position": _grid(12, 1.1 * u.arcsec),
        "axis": ("x", "y"),
        "fwhm": 2 * u.arcsec,
    }
    noise = na.random.normal(
        loc=0,
        scale=2,
        shape_random={"trial": 200} | images.outputs.shape,
        seed=1,
    )
    noisy = dataclasses.replace(images, outputs=noise * u.DN)
    counts, _, _ = esis_jet_paper._dem._resample(images=noisy, **kwargs)
    _, uncertainty, _ = esis_jet_paper._dem._resample(images=images, **kwargs)
    measured = np.square(counts).mean("trial").mean().ndarray
    predicted = np.square(uncertainty).mean().ndarray
    assert np.isclose(measured, predicted, rtol=0.03)


def test_resample_too_sharp(tmp_path: pathlib.Path) -> None:
    """AIA cannot be made sharper than it is."""
    images = _flat(tmp_path, num=20, value=1)
    with pytest.raises(ValueError, match="must not be smaller"):
        esis_jet_paper._dem._resample(
            images=images,
            uncertainty=1 * u.DN,
            position=_grid(6, 1.1 * u.arcsec),
            axis=("x", "y"),
            fwhm=1 * u.arcsec,
        )


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


def test_temperature_response():
    """
    The six AIA channels and XRT respond on the temperatures of the DEM, with
    171 Å peaking near log T = 5.9 and XRT above log T = 6.5.
    """
    response = esis_jet_paper.temperature_response()
    assert response.outputs.shape == {"channel": 7, "temperature": 51}
    assert np.all(response.outputs > 0)
    assert np.allclose(response.inputs, esis_jet_paper.dem().dem.inputs)

    logt = np.log10(response.inputs / u.K)
    peak = logt[np.argmax(response.outputs, axis="temperature")]
    assert 5.8 < peak[{"channel": 2}] < 6.0
    assert peak[{"channel": 6}] > 6.5
