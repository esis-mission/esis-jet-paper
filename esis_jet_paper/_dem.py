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
]

_box = {"detector_x": slice(172, 300), "detector_y": slice(80, 208)}
"""The 128 by 128 pixels of XRT around event E, as in the DEM tutorial of hinode."""

_fwhm_xrt = 2 * u.arcsec
"""The width at half maximum of the core of the point-spread function of XRT."""

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


def _stack(aia: na.AbstractScalar, xrt: na.AbstractScalar) -> na.AbstractScalar:
    """The six AIA channels and XRT along one axis."""
    xrt = na.broadcast_to(xrt.add_axes("channel"), aia[{"channel": slice(1)}].shape)
    return np.concatenate([aia, xrt], axis="channel")


@functools.cache
def dem() -> Inversion:
    """
    The DEM of event E from AIA and XRT for every Al_poly image of XRT from
    18:00 to 18:20 UT, inverted as in the DEM tutorial of hinode.

    For each XRT image, the image of each AIA channel closest to the middle
    of its exposure is blurred to the resolution of XRT and summed onto its
    pixels with :meth:`sdo.aia.Filtergram.resample`.
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
    noise_photon = (variance_xrt.outputs / response_xrt.outputs)[_temperature_noise]

    in_box = na.ScalarArray.zeros(images_xrt.outputs[{"time": 0}].shape) > 0
    in_box[_box] = True
    ratio_noise = images_xrt.ratio_noise(noise_photon, where=~in_box)

    time_aia = images_aia.inputs.time.ndarray
    response_aia = sdo.aia.temperature_response(
        wavelength=esis_jet_paper.channels,
        time=time_aia.min(),
        eve=True,
        chiantifix=True,
    )[_temperature_aia]
    solid_angle_aia = np.square(_plate_scale_aia).to(u.sr)
    outputs_aia = (response_aia.outputs / (solid_angle_aia / u.pix)).to(_unit_response)

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
        counts, uncertainty = aia.resample(
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

        outputs_xrt = response_xrt.outputs / (solid_angle_xrt / u.pix)
        response = na.FunctionArray(
            inputs=response_aia.inputs,
            outputs=np.concatenate(
                [outputs_aia, outputs_xrt.to(_unit_response)],
                axis="channel",
            ),
        )

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
