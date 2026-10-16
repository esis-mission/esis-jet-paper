import aastex
import astropy.units as u
import numpy as np

import esis_jet_paper

__all__ = [
    "variables",
]


def _pending(name: str) -> aastex.Variable:
    """
    A quantity the analysis has not produced yet, marked where it is cited.

    Every number in this article is computed by the analysis, and these are
    the ones it has no answer for yet. They are written into the text as a
    bold ``XX`` rather than guessed at or left out, so that a draft shows
    plainly what is still owed and no placeholder can be mistaken for a
    measurement. ``??`` is avoided since it is what LaTeX prints for an
    unresolved cross-reference, which the tests look for.
    """
    return aastex.Variable(name=name, value=aastex.NoEscape(r"\textbf{XX}"))


def _backgrounds() -> list[aastex.Variable]:
    """
    The numbers in the appendix on the background and in the captions of
    :func:`esis_jet_paper.figures.backgrounds` and
    :func:`esis_jet_paper.figures.dem_backgrounds`.
    """
    figure = esis_jet_paper.figures._backgrounds

    # The plate scale of XRT is the same in every image.
    cdelt = esis_jet_paper.xrt().inputs.cdelt.position[{"time": 0}]
    width = figure.size_narrow * cdelt.x.ndarray.to(u.arcsec)

    return [
        aastex.Variable("backgroundsSizeNarrow", figure.size_narrow),
        aastex.Variable("backgroundsWidthNarrow", np.round(width)),
    ]


def _dem_movie() -> list[aastex.Variable]:
    """The numbers in the caption of :func:`esis_jet_paper.figures.dem_movie`."""
    figure = esis_jet_paper.figures._dem_movie
    module = esis_jet_paper._dem

    time = esis_jet_paper.dem().time
    num = time.size

    def clock(i: int) -> str:
        return time[i].strftime("%H:%M:%S")

    # The plate scale of XRT is the same in every image.
    cdelt = esis_jet_paper.xrt().inputs.cdelt.position[{"time": 0}]
    width = module._size_background * cdelt.x.ndarray.to(u.arcsec)

    return [
        aastex.Variable("demBackgroundSize", module._size_background),
        aastex.Variable("demBackgroundWidth", np.round(width)),
        aastex.Variable(
            "demBackgroundProportion",
            100 * module._proportion_background * u.percent,
        ),
        aastex.Variable("demMovieFrames", num),
        aastex.Variable("demMovieStart", clock(0)),
        aastex.Variable("demMovieStop", clock(num - 1)),
        aastex.Variable("demMovieStill", clock(figure.index_still())),
        aastex.Variable("demMovieFps", figure.fps),
        aastex.Variable("demMovieDuration", round(num / figure.fps) * u.s),
        aastex.Variable("demMovieTemperatureMin", figure.temperature_min),
        aastex.Variable("demMovieTemperatureMax", figure.temperature_max),
        aastex.Variable("demMoviePercentile", figure.percentile),
    ]


def _dem_regions() -> list[aastex.Variable]:
    """The numbers in the caption of :func:`esis_jet_paper.figures.dem_regions`."""
    figure = esis_jet_paper.figures._dem_regions
    regions = figure.inversions().values()
    ratio_aia = [region.ratio_aia for region in regions]
    misfit = max(abs(region.ratio - 1) for region in regions)
    x, y = figure.background
    return [
        aastex.Variable("demRegionsBackgroundX", x * u.arcsec),
        aastex.Variable("demRegionsBackgroundY", y * u.arcsec),
        aastex.Variable("demRegionsBackgroundRadius", figure.radius_background),
        aastex.Variable("demRegionsRatioMin", f"{min(ratio_aia):.1f}"),
        aastex.Variable("demRegionsRatioMax", f"{max(ratio_aia):.1f}"),
        aastex.Variable("demRegionsMisfit", np.ceil(100 * misfit) * u.percent),
    ]


def _lifetime() -> list[aastex.Variable]:
    """
    The lifetime of event E, measured from its light curves by
    :func:`esis_jet_paper.figures._light_curves.lifetime`.
    """
    figure = esis_jet_paper.figures._light_curves
    start, stop = figure.lifetime()
    duration = (stop - start).to(u.min)
    return [
        aastex.Variable("eventDuration", np.round(duration)),
        aastex.Variable("eventStart", start.strftime("%H:%M:%S")),
        aastex.Variable("eventStop", stop.strftime("%H:%M:%S")),
        aastex.Variable(
            "lifetimeFraction", round(100 * figure.fraction_lifetime) * u.percent
        ),
        aastex.Variable("lifetimeQuiet", figure.duration_quiet),
    ]


def _light_curves() -> list[aastex.Variable]:
    """The numbers in the caption of :func:`esis_jet_paper.figures.light_curves`."""
    figure = esis_jet_paper.figures._light_curves
    start, stop = figure.window()
    return [
        aastex.Variable("lightCurvesStart", start.strftime("%H:%M:%S")),
        aastex.Variable("lightCurvesStop", stop.strftime("%H:%M:%S")),
    ]


def _length() -> list[aastex.Variable]:
    """The length of event E, :func:`esis_jet_paper._points.length`."""
    return [
        aastex.Variable("eventLength", np.round(esis_jet_paper._points.length())),
    ]


def _points() -> list[aastex.Variable]:
    """
    The radii of the regions about :data:`esis_jet_paper.points` whose mean
    intensities the figures use, one for the base and the footpoint, and one
    for the spire.
    """
    radii = esis_jet_paper.radii
    return [
        aastex.Variable("radiusPoint", radii["base"]),
        aastex.Variable("radiusSpire", radii["spire"]),
    ]


def _temperature() -> list[aastex.Variable]:
    """
    The peak temperature of event E, that of the DEM of its base from AIA and
    XRT, :func:`esis_jet_paper.figures._dem_regions.temperature_peak`.
    """
    temperature = esis_jet_paper.figures._dem_regions.temperature_peak()
    return [
        aastex.Variable("temperaturePeak", np.round(temperature.to(u.MK), 1)),
    ]


def _temperature_responses() -> list[aastex.Variable]:
    """
    The numbers in the caption of
    :func:`esis_jet_paper.figures.temperature_responses`.
    """
    figure = esis_jet_paper.figures._temperature_responses
    return [
        aastex.Variable("temperatureResponsesMin", f"{figure.temperature_min():.1f}"),
        aastex.Variable("temperatureResponsesMax", f"{figure.temperature_max():.1f}"),
    ]


def _xrt() -> list[aastex.Variable]:
    """The plate scale, the field, and the cadence of the images of XRT."""
    images = esis_jet_paper.xrt()

    # The plate scale of XRT is the same in every image.
    cdelt = images.inputs.cdelt.position[{"time": 0}].x.ndarray.to(u.arcsec)
    width = images.outputs.shape["detector_x"] * cdelt

    time = images.inputs.time.ndarray
    cadence = np.median((time[1:] - time[:~0]).to(u.s))

    return [
        aastex.Variable("xrtPlateScale", np.round(cdelt, 2)),
        aastex.Variable("xrtFieldWidth", np.round(width.to(u.arcmin), 1)),
        aastex.Variable("xrtCadence", np.round(cadence, 1)),
    ]


def variables() -> list[aastex.Variable]:
    """
    A list of LaTeX variables for every numeric quantity cited in the prose.

    Reference these macros in section strings instead of hardcoding numbers so
    that the text stays in sync with the analysis.
    """
    return (
        [
            _pending("velocityBlue"),
            _pending("velocityRed"),
        ]
        + _backgrounds()
        + _dem_movie()
        + _dem_regions()
        + _length()
        + _lifetime()
        + _light_curves()
        + _points()
        + _temperature()
        + _temperature_responses()
        + _xrt()
    )
