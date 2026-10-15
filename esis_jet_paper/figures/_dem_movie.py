import dataclasses
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


@dataclasses.dataclass(frozen=True)
class _Row:
    """
    What one row of the figure draws, from the DEM with or without the
    background subtracted.
    """

    subtract_background: bool
    """Whether the background was subtracted from the intensities first."""

    logt: na.AbstractScalar
    """The log T of each temperature colored in the image."""

    dem: na.AbstractScalar
    """The DEM at each of :attr:`logt` in units of :data:`_scale`."""

    vmax: float
    """The DEM at which the brightness saturates."""

    logt_all: na.AbstractScalar
    """The log T of every temperature of the inversion."""

    curves: dict[str, na.AbstractScalar]
    """
    The DEM in units of :data:`_scale` of the pixel nearest each of
    :data:`esis_jet_paper.points` in every frame.
    """

    median: na.AbstractScalar
    """The median DEM of the pixels inside the field of :func:`_field` in every frame."""


def _row(subtract_background: bool) -> _Row:
    """
    What one row of the figure draws, from the DEM of
    :func:`esis_jet_paper.dem` with or without the background subtracted.

    The brightness saturates at the :data:`percentile` th percentile of the
    DEM of the row over the whole movie.
    The pixel nearest each point is found again in each frame, since each
    XRT image points a little differently.
    """
    inversion = esis_jet_paper.dem(subtract_background)
    logt = np.log10(inversion.dem.inputs / u.K)
    dem = (inversion.dem.outputs / _scale).to(u.dimensionless_unscaled)

    where = (logt >= temperature_min - 1e-6) & (logt <= temperature_max + 1e-6)
    temperature = {"temperature": np.flatnonzero(where.ndarray)}
    shown = dem[temperature]

    position = inversion.position.to(u.arcsec)
    lo, hi = slice(None, -1), slice(1, None)
    center = (
        position[{"detector_x": lo, "detector_y": lo}]
        + position[{"detector_x": hi, "detector_y": lo}]
        + position[{"detector_x": lo, "detector_y": hi}]
        + position[{"detector_x": hi, "detector_y": hi}]
    ) / 4

    curves = {}
    for name, (x, y) in esis_jet_paper.points.items():
        distance = np.square(center.x - x * u.arcsec)
        distance = distance + np.square(center.y - y * u.arcsec)
        index = np.argmin(distance, axis=("detector_x", "detector_y"))
        curves[name] = dem[index]

    # The pixels shown in the image, a reference against which event E stands.
    (xmin, xmax), (ymin, ymax) = _field()
    inside = (center.x >= xmin * u.arcsec) & (center.x <= xmax * u.arcsec)
    inside = inside & (center.y >= ymin * u.arcsec) & (center.y <= ymax * u.arcsec)
    median = np.nanmedian(
        np.where(inside, dem, np.nan),
        axis=("detector_x", "detector_y"),
    )

    return _Row(
        subtract_background=subtract_background,
        logt=logt[temperature],
        dem=shown,
        vmax=float(np.nanpercentile(shown.ndarray, percentile)),
        logt_all=logt,
        curves=curves,
        median=median,
    )


def _draw(
    axs: np.ndarray,
    i: int,
    row: _Row,
    field: tuple[tuple[float, float], tuple[float, float]],
    limits: tuple[float, float],
) -> None:
    """
    Draw the false-color DEM of frame `i` of `row` on the image and colorbar
    axes, and the DEM at each of :data:`esis_jet_paper.points` on the third
    axes, within the `field` of :func:`_field` and between the DEM `limits`.

    The row with the background subtracted goes beneath the other, which
    carries the time and the legend. It leaves out the median, since the
    median pixel is no brighter than its background.
    """
    inversion = esis_jet_paper.dem()
    position = inversion.position[{"time": i}]
    dem = row.dem[{"time": i}]
    logt_all = row.logt_all

    for ax in axs:
        ax.clear()
    colorbar = na.plt.rgbmesh(
        row.logt,
        position,
        C=dem,
        axis_wavelength="temperature",
        ax=axs[0],
        vmin=0,
        vmax=row.vmax,
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

    if row.subtract_background:
        axs[0].set_title("background subtracted")
        axs[0].set_xlabel("helioprojective $x$ (arcsec)")
        axs[2].set_xlabel(r"$\log_{10} T$")
    else:
        time = inversion.time[i].strftime("%H:%M:%S")
        axs[0].set_title(f"{time} UT")
        # Blank, rather than left to the unit of the coordinates.
        axs[0].set_xlabel("")
    axs[0].set_xlim(field[0])
    axs[0].set_ylim(field[1])
    axs[0].set_aspect("equal")
    axs[0].set_ylabel("helioprojective $y$ (arcsec)")
    axs[1].set_xlabel(r"DEM ($10^{27}\,\mathrm{cm^{-5}}$)")
    axs[1].set_ylabel(r"$\log_{10} T$")
    axs[1].yaxis.tick_right()
    axs[1].yaxis.set_label_position("right")

    # The range of temperatures colored in the image.
    axs[2].axvspan(temperature_min, temperature_max, color="0.9", linewidth=0)
    for name, (x, y) in esis_jet_paper.points.items():
        axs[0].plot(
            x,
            y,
            marker="o",
            markersize=5,
            markeredgewidth=0.8,
            markerfacecolor="none",
            markeredgecolor="white",
        )
        axs[0].annotate(
            name,
            xy=(x, y),
            xytext=(6, 4),
            textcoords="offset points",
            color="white",
        )
        curve = row.curves[name][{"time": i}]
        # XRT saturated in this pixel, which left it without a DEM.
        label = f"{name}, saturated" if np.all(np.isnan(curve.ndarray)) else name
        na.plt.plot(
            logt_all,
            curve,
            axis="temperature",
            ax=axs[2],
            color="black",
            linestyle=esis_jet_paper.linestyles[name],
            label=label,
        )
    if not row.subtract_background:
        # Last in the legend, but beneath the points, above the shading.
        na.plt.plot(
            logt_all,
            row.median[{"time": i}],
            axis="temperature",
            ax=axs[2],
            color="0.5",
            label="median",
            zorder=1.5,
        )
        axs[2].legend(loc="upper right")
    axs[2].set_yscale("log")
    axs[2].set_xlim(float(logt_all.min().ndarray), float(logt_all.max().ndarray))
    axs[2].set_ylim(limits)
    axs[2].set_ylabel(r"DEM ($10^{27}\,\mathrm{cm^{-5}}$)")
    axs[2].yaxis.tick_right()
    axs[2].yaxis.set_label_position("right")


def dem_movie() -> aastex.Figure:
    """
    The DEM of event E as a false-color image, at one time in the PDF and
    for every XRT image from 18:00 to 18:20 UT in the movie, with and
    without the background subtracted.
    """
    inversion = esis_jet_paper.dem()
    rows = [_row(subtract_background) for subtract_background in (False, True)]
    field = _field()
    # Both rows share the limits of the DEM, which hold every frame.
    peak = max(
        float(np.nanmax(curve.ndarray)) for row in rows for curve in row.curves.values()
    )
    limits = (peak / 1e3, 2 * peak)

    def draw(i: int) -> None:
        for ax, row in zip(axs, rows):
            _draw(ax, i, row, field, limits)

    # The movie is drawn in the same fonts as the still, even when it is
    # made outside of :func:`esis_jet_paper.document`.
    with plt.rc_context(esis_jet_paper.rc):
        fig, axs = plt.subplots(
            nrows=2,
            ncols=3,
            figsize=(aastex.text_width_inches, 0.8 * aastex.text_width_inches),
            gridspec_kw={"width_ratios": [0.46, 0.06, 0.48]},
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
            draw(0)
            fig.canvas.draw()
            for i in range(inversion.time.size):
                draw(i)
                writer.grab_frame()

        draw(index_still())

    result = aastex.FigureStar(
        "fig:demMovie",
        position="t",
        animation=aastex.Animation(movie, url=esis_jet_paper.url(movie.name)),
    )
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
The \DEM\ of event E from the six \EUV\ channels of \AIA\ and from \XRT\ Al\_poly at
\demMovieStill~UT, as a false-color image (left), inverted from the intensities as observed
(top) and with the background of each pixel subtracted first (bottom): in each channel, the
mean of the \demBackgroundSize\ by \demBackgroundSize\ pixels of \XRT\
(\demBackgroundWidth) around it, without the brightest and the faintest
\demBackgroundProportion\ of them, which leaves out event E.
Each pixel is colored as if the \DEM\ were the spectrum of the light it emits, with
$\log_{10} T$ from \demMovieTemperatureMin\ to \demMovieTemperatureMax\ mapped onto the
visible spectrum, from violet for the coolest plasma to red for the hottest (middle).
Every temperature and every frame of a row shares one linear scale, up to the
\demMoviePercentile th percentile of the row over the whole movie, so the brightness of a
pixel is how much plasma it has and its color is at what temperature.
White pixels are those where \XRT\ saturated, which have no \DEM, and black pixels in the
bottom row are those no brighter than their background in any channel.
The \DEM\ of the pixel nearest each of the three circled points, the base of event E, the
hottest part of its spire, and its northern footpoint, is plotted over every temperature of
the inversion (right),
against the median \DEM\ of the pixels in the image (gray line, top only, since the median
pixel is no brighter than its background), with the temperatures colored in the image shaded
gray.
The animation shows the \DEM\ for each of the \demMovieFrames\ \XRT\ images which began
from \demMovieStart\ to \demMovieStop~UT, at \demMovieFps\ frames per second, and runs
for \demMovieDuration.
"""))
    return result
