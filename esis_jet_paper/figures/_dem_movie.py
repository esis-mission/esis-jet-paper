import pathlib

import aastex
import astropy.time
import astropy.units as u
import matplotlib.animation
import matplotlib.colors
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np

import esis_jet_paper

__all__ = [
    "dem_movie",
    "fps",
    "index_still",
    "percentile",
    "temperature_max",
    "temperature_min",
    "time_still",
]

time_still = astropy.time.Time("2019-09-30T18:08:00")
"""The time of the frame shown in the PDF, the XRT image which begins closest to it."""

fps = 4
"""The number of frames per second of the movie."""

temperature_min = 5.6
"""The lowest log T shown, below which the DEM rests on AIA 335 alone."""

temperature_max = 6.5
"""
The highest log T shown, above which lies only about 3% of the emission
measure of the movie, so that the colors spread over the plasma there is.
"""

_scale = 1e27 / u.cm**5
"""The unit the DEM is shown in, so that the colorbar needs no offset."""

percentile = 99.5
"""The percentile of the DEM over the whole movie at which the brightness saturates."""


def index_still() -> int:
    """The index of the frame shown in the PDF."""
    time = esis_jet_paper.dem().time
    return int(np.argmin(np.abs((time - time_still).to(u.s))))


def _field() -> tuple[tuple[float, float], tuple[float, float]]:
    """
    The helioprojective :math:`x` and :math:`y` limits, in arcseconds, of the
    field that every frame fills.

    Each XRT image points a little differently, so a frame drawn to its own
    limits would carry that jitter onto the Sun, and its slightly rolled edges
    would leave slivers of the background showing.
    """
    position = esis_jet_paper.dem().position
    x = position.x.to(u.arcsec)
    y = position.y.to(u.arcsec)
    xlim = (
        float(x[{"detector_x": 0}].max().ndarray.value),
        float(x[{"detector_x": -1}].min().ndarray.value),
    )
    ylim = (
        float(y[{"detector_y": 0}].max().ndarray.value),
        float(y[{"detector_y": -1}].min().ndarray.value),
    )
    return xlim, ylim


def _shown() -> tuple[
    na.AbstractScalar,
    na.AbstractScalar,
    float,
    tuple[tuple[float, float], tuple[float, float]],
]:
    """
    The log T of each temperature shown, the DEM there in units of
    :data:`_scale`, the value at which the brightness saturates, and the
    limits of the field shown, from :func:`_field`.
    """
    inversion = esis_jet_paper.dem()
    logt = np.log10(inversion.dem.inputs / u.K)
    where = (logt >= temperature_min - 1e-6) & (logt <= temperature_max + 1e-6)
    index = {"temperature": np.flatnonzero(where.ndarray)}
    dem = (inversion.dem.outputs / _scale).to(u.dimensionless_unscaled)
    dem = dem[index]
    vmax = float(np.nanpercentile(dem.ndarray, percentile))
    return logt[index], dem, vmax, _field()


def _draw(
    axs: np.ndarray,
    i: int,
    logt: na.AbstractScalar,
    dem: na.AbstractScalar,
    vmax: float,
    field: tuple[tuple[float, float], tuple[float, float]],
) -> None:
    """
    Draw the false-color DEM of frame `i` on the image and colorbar axes,
    given what :func:`_shown` returns.
    """
    inversion = esis_jet_paper.dem()
    position = inversion.position[{"time": i}]
    dem = dem[{"time": i}]

    for ax in axs:
        ax.clear()
    colorbar = na.plt.rgbmesh(
        logt,
        position,
        C=dem,
        axis_wavelength="temperature",
        ax=axs[0],
        vmin=0,
        vmax=vmax,
        # in the PDF, so that no seams show between the pixels
        rasterized=True,
    )
    # The pixels where XRT saturated, which have no DEM.
    missing = np.isnan(dem).any("temperature")
    na.plt.pcolormesh(
        position,
        C=np.where(missing, 1, np.nan),
        ax=axs[0],
        cmap=matplotlib.colors.ListedColormap(["white"]),
        rasterized=True,
    )
    na.plt.pcolormesh(
        C=colorbar,
        axis_rgb="temperature",
        ax=axs[1],
        rasterized=True,
    )

    time = inversion.time[i].strftime("%H:%M:%S")
    axs[0].set_title(f"{time} UT")
    axs[0].set_xlim(field[0])
    axs[0].set_ylim(field[1])
    axs[0].set_aspect("equal")
    axs[0].set_xlabel("helioprojective $x$ (arcsec)")
    axs[0].set_ylabel("helioprojective $y$ (arcsec)")
    axs[1].set_xlabel(r"DEM ($10^{27}\,\mathrm{cm^{-5}}$)")
    axs[1].set_ylabel(r"$\log_{10} T$")
    axs[1].yaxis.tick_right()
    axs[1].yaxis.set_label_position("right")


def dem_movie() -> aastex.Figure:
    """
    The DEM of event E as a false-color image, at one time in the PDF and
    for every XRT image from 18:00 to 18:20 UT in the movie.
    """
    inversion = esis_jet_paper.dem()
    shown = _shown()

    # The movie is drawn in the same fonts as the still, even when it is
    # made outside of :func:`esis_jet_paper.document`.
    with plt.rc_context(esis_jet_paper.rc):
        fig, axs = plt.subplots(
            ncols=2,
            figsize=(aastex.column_width_inches, 0.85 * aastex.column_width_inches),
            gridspec_kw={"width_ratios": [0.88, 0.12]},
            constrained_layout=True,
        )

        # Beside the PDF, where `aastex` would otherwise copy it.
        movie = pathlib.Path(esis_jet_paper.__file__).parent / "dem-event-e.mp4"
        writer = matplotlib.animation.FFMpegWriter(
            fps=fps,
            codec="h264",
            extra_args=["-pix_fmt", "yuv420p"],
        )
        with writer.saving(fig, movie, dpi=300):
            # Constrained layout settles on the second draw of axes with a
            # fixed aspect, so draw once before the first frame is recorded.
            _draw(axs, 0, *shown)
            fig.canvas.draw()
            for i in range(inversion.time.size):
                _draw(axs, i, *shown)
                writer.grab_frame()

        _draw(axs, index_still(), *shown)

    result = aastex.Figure(
        "fig:demMovie",
        position="!htb",
        animation=aastex.Animation(movie, url=esis_jet_paper.url(movie.name)),
    )
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
The \DEM\ of event E from the six \EUV\ channels of \AIA\ and from \XRT\ Al\_poly at
\demMovieStill~UT, as a false-color image.
Each pixel is colored as if the \DEM\ were the spectrum of the light it emits, with
$\log_{10} T$ from \demMovieTemperatureMin\ to \demMovieTemperatureMax\ mapped onto the
visible spectrum, from violet for the coolest plasma to red for the hottest (right).
Every temperature and every frame shares one linear scale, up to the
\demMoviePercentile th percentile of the whole movie, so the brightness of a pixel is how
much plasma it has and its color is at what temperature.
White pixels are those where \XRT\ saturated, which have no \DEM.
The animation shows the \DEM\ for each of the \demMovieFrames\ \XRT\ images which began
from \demMovieStart\ to \demMovieStop~UT, at \demMovieFps\ frames per second, and runs
for \demMovieDuration.
"""))
    return result
