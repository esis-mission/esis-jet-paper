import aastex
import astropy.units as u

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


def _dem_movie() -> list[aastex.Variable]:
    """The numbers in the caption of :func:`esis_jet_paper.figures.dem_movie`."""
    figure = esis_jet_paper.figures._dem_movie

    time = esis_jet_paper.dem().time
    num = time.size

    def clock(i: int) -> str:
        return time[i].strftime("%H:%M:%S")

    return [
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


def _light_curves() -> list[aastex.Variable]:
    """The numbers in the caption of :func:`esis_jet_paper.figures.light_curves`."""
    figure = esis_jet_paper.figures._light_curves
    start, stop = figure.window()
    return [
        aastex.Variable("lightCurvesStart", start.strftime("%H:%M:%S")),
        aastex.Variable("lightCurvesStop", stop.strftime("%H:%M:%S")),
        aastex.Variable("lightCurvesRadius", figure.radius),
    ]


def variables() -> list[aastex.Variable]:
    """
    A list of LaTeX variables for every numeric quantity cited in the prose.

    Reference these macros in section strings instead of hardcoding numbers so
    that the text stays in sync with the analysis.
    """
    return (
        [
            _pending("eventDuration"),
            _pending("eventLength"),
            _pending("velocityBlue"),
            _pending("velocityRed"),
            _pending("temperaturePeak"),
        ]
        + _dem_movie()
        + _light_curves()
    )
