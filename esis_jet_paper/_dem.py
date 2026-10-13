import dataclasses
import functools

import astropy.time
import astropy.units as u
import hinode
import named_arrays as na
import numpy as np
import sdo
import utu

import esis_jet_paper

__all__ = [
    "Inversion",
    "dem",
    "temperature_response",
]

_box = {"detector_x": slice(172, 300), "detector_y": slice(105, 233)}
"""
The 128 by 128 pixels of XRT around event E, centered between its base and
its northern footpoint, which the box of the DEM tutorial of hinode cuts off.
"""

_fwhm_xrt = 2 * u.arcsec
"""The width at half maximum of the core of the point-spread function of XRT."""

_fwhm_aia = 1.3 * u.arcsec
"""The width at half maximum of the core of the point-spread function of AIA."""

_seed = 0
"""The seed of the white noise which finds how much resampling averages down the noise of AIA."""

_temperature_aia = {"temperature": slice(20, 71)}
"""The temperatures of the AIA responses from log T = 5.0 to 7.5."""

_temperature_xrt = {"temperature": slice(0, 51)}
"""The temperatures of the XRT response from log T = 5.0 to 7.5."""

_temperature_noise = {"temperature": 26}
"""log T = 6.3, near the temperature of most of the plasma, where the photon noise of XRT is taken."""

_plate_scale_aia = 0.6 * u.arcsec
"""The plate scale of the registered AIA images."""

_unit_response = u.DN * u.cm**5 / u.s / u.sr
"""The unit of the temperature responses, per steradian like the intensities."""


@dataclasses.dataclass(frozen=True)
class Inversion:
    """The DEM of event E for every XRT image, and how well it fits."""

    time: astropy.time.Time
    """The start of each XRT image, along ``time``."""

    position: na.AbstractCartesian2dVectorArray
    """The helioprojective coordinates of the vertices of the pixels of each image."""

    dem: na.FunctionArray
    """The DEM of each pixel per unit log T, along ``temperature``."""

    chi2: na.AbstractScalar
    """The reduced chi squared of each pixel, -1 where it has no DEM."""

    saturated: na.AbstractScalar
    """Whether XRT saturated in each pixel, which leaves it without a DEM."""

    ratio_noise: float
    """The variance of the noise of XRT measured over the sequence, over its model."""


def _resample(
    images: sdo.aia.Filtergram,
    uncertainty: na.AbstractScalar,
    position: na.AbstractCartesian2dVectorArray,
    axis: tuple[str, str],
    fwhm: u.Quantity,
) -> tuple[na.AbstractScalar, na.AbstractScalar]:
    """
    Blur AIA images to the resolution of another instrument and sum them
    onto its pixels, along with their uncertainty.

    The images are blurred by a Gaussian whose width at half its maximum is
    the difference in quadrature between `fwhm` and :data:`_fwhm_aia`, so
    that a point source is as wide as the other instrument sees it, and then
    summed onto the new pixels by conservative regridding, which keeps the
    total signal.

    The variance of each pixel is summed onto the new pixels the same way,
    which alone would overestimate the noise, since the blur averages
    neighboring pixels together, and the pixels which straddle two new pixels
    are split between them.
    How much both average the noise down is found by blurring and resampling
    white noise of unit variance, and the summed variance of each image is
    scaled by it.

    Parameters
    ----------
    images
        The registered AIA images.
    uncertainty
        The one-sigma uncertainty of each pixel of `images`.
    position
        The helioprojective coordinates of the vertices of the new pixels.
    axis
        The two logical axes of `position` along which the new pixels are
        arranged.
    fwhm
        The full width at half maximum of the point-spread function of the
        new pixels, which must not be smaller than :data:`_fwhm_aia`.

    Returns
    -------
    counts
        The signal of each new pixel, in DN.
    uncertainty
        The one-sigma uncertainty of `counts`.
    """
    axis_detector = (images.axis_detector_x, images.axis_detector_y)

    difference = np.square(fwhm) - np.square(_fwhm_aia)
    if np.any(difference < 0):
        raise ValueError(
            f"`fwhm`, {fwhm}, must not be smaller than that of AIA, {_fwhm_aia}."
        )
    sigma = np.sqrt(difference) / (2 * np.sqrt(2 * np.log(2)))

    def blur(a: na.AbstractScalar) -> na.AbstractScalar:
        if np.all(sigma == 0):
            return a
        cdelt = images.inputs.cdelt.position
        scale = (np.abs(cdelt.x).mean() + np.abs(cdelt.y).mean()) / 2
        scale = scale.to(u.arcsec)
        # out to four times the width of the Gaussian, beyond which it is
        # less than a ten-thousandth of its peak
        ratio = na.as_named_array(4 * sigma / scale).to(u.dimensionless_unscaled)
        num = int(np.ceil(ratio.max().ndarray.value))
        x = na.arange(-num, num + 1, axis=images.axis_detector_x) * scale
        y = na.arange(-num, num + 1, axis=images.axis_detector_y) * scale
        kernel = np.exp(-(np.square(x) + np.square(y)) / (2 * np.square(sigma)))
        kernel = kernel / kernel.sum(axis_detector)
        return na.convolve(a, kernel, axis=axis_detector)

    weights = na.regridding.weights(
        coordinates_input=images.inputs.position,
        coordinates_output=position,
        axis_input=axis_detector,
        axis_output=axis,
        method="conservative",
    )

    def regrid(a: na.AbstractScalar) -> na.AbstractScalar:
        return na.regridding.regrid_from_weights(*weights, values_input=a)

    counts = regrid(blur(images.outputs))
    variance = regrid(np.square(uncertainty))

    shape = images.outputs.shape
    noise = na.random.normal(0, 1, shape_random=shape, seed=_seed)
    noise = regrid(blur(noise))
    ones = regrid(na.ScalarArray.ones(shape))
    reduction = np.square(noise).mean(axis) / ones.mean(axis)

    return counts, np.sqrt(reduction * variance)


def _stack(aia: na.AbstractScalar, xrt: na.AbstractScalar) -> na.AbstractScalar:
    """The six AIA channels and XRT along one axis."""
    xrt = na.broadcast_to(xrt.add_axes("channel"), aia[{"channel": slice(1)}].shape)
    return np.concatenate([aia, xrt], axis="channel")


@functools.cache
def temperature_response() -> na.FunctionArray:
    """
    The temperature response of each channel from which the DEM of event E
    is inverted, per steradian, from log T = 5.0 to 7.5: the EUV channels of
    AIA in :data:`esis_jet_paper.channels` and then XRT Al_poly, along
    ``channel``.

    The response of AIA is that of SolarSoft at the time of the first AIA
    image, normalized to EVE and with the empirical correction for the
    emission CHIANTI is missing.
    The response of XRT is that of xrtpy, with the contamination on the date
    of the first XRT image.
    """
    images_xrt = esis_jet_paper.xrt()
    images_aia = esis_jet_paper.aia()

    response_aia = sdo.aia.temperature_response(
        wavelength=esis_jet_paper.channels,
        time=images_aia.inputs.time.ndarray.min(),
        eve=True,
        chiantifix=True,
    )[_temperature_aia]
    response_xrt = hinode.xrt.temperature_response(
        filter="Al_poly",
        time=images_xrt.inputs.time.ndarray[0],
        axis_filter="channel",
    )[_temperature_xrt]

    solid_angle_aia = np.square(_plate_scale_aia).to(u.sr)
    # The plate scale of XRT is the same in every image.
    cdelt = images_xrt.inputs.cdelt.position[{"time": 0}]
    solid_angle_xrt = (cdelt.x * cdelt.y).to(u.sr)

    outputs_aia = response_aia.outputs / (solid_angle_aia / u.pix)
    outputs_xrt = response_xrt.outputs / (solid_angle_xrt / u.pix)
    return na.FunctionArray(
        inputs=response_aia.inputs,
        outputs=np.concatenate(
            [outputs_aia.to(_unit_response), outputs_xrt.to(_unit_response)],
            axis="channel",
        ),
    )


@functools.cache
def dem() -> Inversion:
    """
    The DEM of event E from AIA and XRT for every Al_poly image of XRT from
    18:00 to 18:20 UT, inverted as in the DEM tutorial of hinode.

    For each XRT image, the image of each AIA channel closest to the middle
    of its exposure is blurred to the resolution of XRT and summed onto its
    pixels with :func:`_resample`.
    The uncertainty of XRT is scaled to the noise measured over the whole
    sequence by :meth:`hinode.xrt.Filtergram.ratio_noise`, away from the jet.
    The pixels where XRT saturated are left without a DEM.
    """
    images_xrt = esis_jet_paper.xrt()
    images_aia = esis_jet_paper.aia()

    time_xrt = images_xrt.inputs.time.ndarray

    response_xrt = hinode.xrt.temperature_response(
        filter="Al_poly",
        time=time_xrt[0],
        axis_filter="channel",
    )[_temperature_xrt]
    variance_xrt = hinode.xrt.temperature_response(
        filter="Al_poly",
        time=time_xrt[0],
        variance=True,
        axis_filter="channel",
    )[_temperature_xrt]
    # One factor, without the axis the response of XRT shares with AIA,
    # so that the ratio of the noise is one number.
    noise_photon = (variance_xrt.outputs / response_xrt.outputs)[
        _temperature_noise | {"channel": 0}
    ]

    in_box = na.ScalarArray.zeros(images_xrt.outputs[{"time": 0}].shape) > 0
    in_box[_box] = True
    ratio_noise = images_xrt.ratio_noise(noise_photon, where=~in_box)

    time_aia = images_aia.inputs.time.ndarray
    response = temperature_response()

    position = []
    dems = []
    chi2s = []
    saturated = []
    for i in range(time_xrt.size):
        xrt = images_xrt[{"time": i}][_box]
        middle = xrt.inputs.time.ndarray + xrt.timedelta.ndarray / 2
        offset = na.ScalarArray(
            ndarray=(time_aia - middle).to(u.s),
            axes=images_aia.inputs.time.axes,
        )
        offset = offset + images_aia.timedelta / 2
        aia = images_aia[np.argmin(np.abs(offset), axis="time")]

        position_xrt = xrt.inputs.position.to(u.arcsec)
        counts, uncertainty = _resample(
            images=aia,
            uncertainty=sdo.aia.uncertainty(
                counts=aia.outputs,
                wavelength=aia.inputs.wavelength,
            ),
            position=position_xrt,
            axis=("detector_x", "detector_y"),
            fwhm=_fwhm_xrt,
        )

        cdelt = xrt.inputs.cdelt.position
        solid_angle_xrt = (cdelt.x * cdelt.y).to(u.sr)

        intensity_aia = counts / aia.timedelta / solid_angle_xrt
        uncertainty_aia = uncertainty / aia.timedelta / solid_angle_xrt

        # NaN where XRT saturated, which leaves the pixel without a DEM
        unit = xrt.outputs.unit
        intensity_xrt = xrt.outputs + np.where(xrt.saturated, np.nan, 0) * unit
        intensity_xrt = intensity_xrt / solid_angle_xrt
        uncertainty_xrt = xrt.uncertainty(noise_photon) / solid_angle_xrt
        uncertainty_xrt = np.sqrt(ratio_noise) * uncertainty_xrt

        d, c = utu.dem.plowman(
            intensity=_stack(intensity_aia, intensity_xrt),
            uncertainty=_stack(uncertainty_aia, uncertainty_xrt),
            response=response,
            axis_channel="channel",
            axis_temperature="temperature",
        )

        position.append(position_xrt)
        dems.append(d.outputs)
        chi2s.append(c)
        saturated.append(xrt.saturated)

    return Inversion(
        time=time_xrt,
        position=na.stack(position, axis="time"),
        dem=na.FunctionArray(
            inputs=d.inputs,
            outputs=na.stack(dems, axis="time"),
        ),
        chi2=na.stack(chi2s, axis="time"),
        saturated=na.stack(saturated, axis="time"),
        ratio_noise=float(ratio_noise.ndarray),
    )
