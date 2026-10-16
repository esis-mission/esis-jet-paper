import dataclasses
import functools

import aastex
import astropy.units as u
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np
import utu

import esis_jet_paper

__all__ = [
    "Region",
    "background",
    "dem_regions",
    "inversions",
    "radius_background",
    "temperature_peak",
]

background = (95, -10)
"""
The helioprojective coordinates, in arcseconds, of the center of the
background region: quiet network west of event E, away from the loops east of
it and from the dark spots in the images of XRT.
"""

radius_background = 5 * u.arcsec
"""The radius of the background region."""

_axis = ("detector_x", "detector_y")
"""The axes along which the pixels of every image are arranged."""

_scale = 1e27 / u.cm**5
"""The unit the DEM is shown in, the same as in the DEM movie."""

_label_esis = r"with ESIS, to come"
"""The label of the DEM with the lines of ESIS, whose line list is not ready yet."""


@dataclasses.dataclass(frozen=True)
class Region:
    """The DEMs of one region at the time of the still of the DEM movie."""

    dem_aia: na.FunctionArray
    """The DEM from the EUV channels of AIA alone."""

    dem: na.FunctionArray
    """The DEM from AIA and XRT."""

    ratio_aia: float
    """The ratio of the XRT intensity :attr:`dem_aia` predicts to that observed."""

    ratio: float
    """The ratio of the XRT intensity :attr:`dem` predicts to that observed."""


def _regions() -> dict[str, tuple[tuple[float, float], u.Quantity]]:
    """
    The center, in arcseconds, and the radius of each region: those of
    :data:`esis_jet_paper.points` and the background.
    """
    result = {
        name: (point, esis_jet_paper.radii[name])
        for name, point in esis_jet_paper.points.items()
    }
    result["background"] = (background, radius_background)
    return result


def _mean(
    observation: "esis_jet_paper._dem._Observation",
    center: tuple[float, float],
    radius: u.Quantity,
) -> tuple[na.AbstractScalar, na.AbstractScalar]:
    """
    The mean intensity in each channel of the pixels of `observation` whose
    centers lie within `radius` of `center`, and its uncertainty.

    The blur which brings AIA to the resolution of XRT correlates the noise of
    neighboring pixels, so the variance of their sum is the sum of their
    variances over the reduction of :func:`esis_jet_paper._dem._resample`.
    That overestimates it for a region not much wider than the blur, like
    that of the spire.
    """
    x, y = center
    position = observation.position.cell_centers(axis=_axis)
    distance = np.square(position.x - x * u.arcsec)
    distance = np.sqrt(distance + np.square(position.y - y * u.arcsec))
    inside = distance <= radius
    num = inside.sum(_axis)

    intensity = np.where(inside, observation.intensity, 0).sum(_axis) / num
    variance = np.square(observation.uncertainty) / observation.reduction
    variance = np.where(inside, variance, 0).sum(_axis)
    return intensity, np.sqrt(variance) / num


@functools.cache
def inversions() -> dict[str, Region]:
    """
    The DEMs of each region at the time of the still of the DEM movie, from
    AIA alone and from AIA and XRT, inverted from the mean intensities of
    :func:`_mean`, keyed by the name of the region.
    """
    index = esis_jet_paper.figures._dem_movie.index_still()
    observation = esis_jet_paper._dem._observe(index)
    response = esis_jet_paper.temperature_response()
    num_aia = esis_jet_paper.channels.shape["channel"]
    aia = {"channel": slice(num_aia)}
    xrt = {"channel": num_aia}

    def ratio(
        dem: na.FunctionArray,
        intensity: na.AbstractScalar,
    ) -> float:
        # The intensity as the inversion models it, with the DEM and the
        # response both linear in log T between the temperatures.
        emission_measure = utu.dem.emission_measure(dem, "temperature")
        predicted = emission_measure * response.outputs[xrt]
        predicted = predicted.sum("temperature")
        ratio = (predicted / intensity[xrt]).to(u.dimensionless_unscaled)
        return float(ratio.ndarray)

    result = {}
    for name, (center, radius) in _regions().items():
        intensity, uncertainty = _mean(observation, center, radius)
        dem_aia, _ = utu.dem.plowman(
            intensity=intensity[aia],
            uncertainty=uncertainty[aia],
            response=response[aia],
            axis_channel="channel",
            axis_temperature="temperature",
        )
        dem, _ = utu.dem.plowman(
            intensity=intensity,
            uncertainty=uncertainty,
            response=response,
            axis_channel="channel",
            axis_temperature="temperature",
        )
        result[name] = Region(
            dem_aia=dem_aia,
            dem=dem,
            ratio_aia=ratio(dem_aia, intensity),
            ratio=ratio(dem, intensity),
        )
    return result


def temperature_peak() -> u.Quantity:
    """
    The temperature at which the DEM of the base of event E from AIA and XRT,
    that of :func:`inversions`, peaks.
    """
    dem = inversions()["base"].dem
    index = np.argmax(dem.outputs, axis="temperature")
    return dem.inputs[index].ndarray


def dem_regions() -> aastex.Figure:
    """
    The DEMs of the base, the spire, the northern footpoint of event E, and of
    a background region, at the time of the still of the DEM movie, from AIA
    alone and from AIA and XRT, with a line kept for ESIS.
    """
    regions = inversions()
    names = list(regions)

    fig, axs = plt.subplots(
        nrows=2,
        ncols=2,
        sharex=True,
        sharey=True,
        figsize=(aastex.column_width_inches, 1.0 * aastex.column_width_inches),
        constrained_layout=True,
    )
    axs = axs.ravel()

    def plot(ax: plt.Axes, dem: na.FunctionArray, **kwargs) -> None:
        na.plt.plot(
            np.log10(dem.inputs / u.K),
            (dem.outputs / _scale).to(u.dimensionless_unscaled),
            axis="temperature",
            ax=ax,
            **kwargs,
        )

    peak = 0
    for ax, name in zip(axs, names):
        region = regions[name]
        plot(ax, region.dem, color="black", label="AIA + XRT")
        plot(ax, region.dem_aia, color="black", linestyle="--", label="AIA alone")
        if name != "background":
            # Beneath the DEMs of the region.
            plot(
                ax,
                regions["background"].dem,
                color="0.6",
                label="background",
                zorder=1.5,
            )
        # Kept for the DEM with the lines of ESIS, whose line list is not
        # ready yet.
        ax.plot([], [], color=esis_jet_paper.color_esis, label=_label_esis)
        ax.set_title(name)
        for dem in [region.dem_aia, region.dem]:
            peak = max(peak, float((dem.outputs / _scale).max().ndarray))

    logt = np.log10(regions[names[0]].dem.inputs / u.K)
    axs[0].set_yscale("log")
    # Three decades, as in the DEM movie.
    axs[0].set_ylim(peak / 1e3, 2 * peak)
    axs[0].set_xlim(float(logt.min().ndarray), float(logt.max().ndarray))
    for ax in axs[2:]:
        ax.set_xlabel(r"$\log_{10} T$")
    for ax in axs[::2]:
        ax.set_ylabel(r"DEM ($10^{27}\,\mathrm{cm^{-5}}$)")

    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside upper center", ncols=2)

    result = aastex.Figure("fig:demRegions", position="t")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
The \DEMs\ of the base of event E, the hottest part of its spire, its northern footpoint,
and a background region of network at \demMovieStill~UT, the time of the still of
Figure~\ref{fig:demMovie}, each inverted from the mean intensities of the pixels within
\radiusPoint\ of the point, \radiusSpire\ for the spire, or within
\demRegionsBackgroundRadius\ of (\demRegionsBackgroundX, \demRegionsBackgroundY) for the
background, from the six \EUV\ channels of \AIA\ alone (dashed) and with \XRT\ Al\_poly
(solid).
The \DEM\ of the background from \AIA\ and \XRT\ is repeated in each panel (gray).
The \DEMs\ from \AIA\ alone predict \demRegionsRatioMin\ to \demRegionsRatioMax\ times the
\XRT\ intensity observed, since \AIA\ alone leaves room for a tail of hot plasma which
\XRT\ rules out, and those with \XRT\ predict it to within \demRegionsMisfit.
\roy{The \DEMs\ with the \ESIS\ lines are left out until the \ESIS\ line list is ready.}
"""))
    return result
