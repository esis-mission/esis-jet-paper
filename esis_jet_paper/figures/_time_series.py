import dataclasses
import functools
import pathlib
from collections.abc import Callable

import aastex
import astropy.time
import astropy.units as u
import matplotlib.animation
import matplotlib.cm
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.ticker
import named_arrays as na
import numpy as np
import sdo
import sunpy.visualization.colormaps.color_tables

import esis_jet_paper

__all__ = [
    "exposures_esis",
    "frames",
    "index_still",
    "limit",
    "percentile_min",
    "time_series",
]

exposures_esis = astropy.time.Time(["2019-09-30T18:06:11.6", "2019-09-30T18:11:11.6"])
"""The start of the first exposure of ESIS and the end of its last."""

percentile_min = 1
"""
The percentile of the intensity of each channel, over the field in every image,
at which the brightness bottoms out.
It tops out at the percentile of the DEM movie.
"""

limit = 100 * u.G
"""The magnetic field at which the colors of the magnetograms saturate."""

_axis = ("detector_x", "detector_y")
"""The axes along which the pixels of every image are arranged."""

_cadence_hmi = 45 * u.s
"""
The cadence of the magnetograms of HMI.
The DATE-OBS of each is half of it before its T_OBS, the time it stands for.
"""

_label_esis = r"ESIS O\,\textsc{v}"
"""The label of the panel of ESIS."""

_name_movie = "time-series-event-e.mp4"
"""The name of the file of the movie."""

_dpi_movie = 200
"""The resolution of the movie, in pixels per inch of the figure."""


@dataclasses.dataclass(frozen=True)
class _Panel:
    """The images of one instrument, cut down to the field of the DEM movie."""

    label: str
    """The name of the instrument, and of its channel or filter."""

    position: na.AbstractCartesian2dVectorArray
    """The helioprojective coordinates of the vertices of every pixel."""

    intensity: na.AbstractScalar
    """What each pixel shows, in the unit of :attr:`label_colorbar`, without it."""

    time: astropy.time.Time
    """The middle of each exposure."""

    cmap: str | matplotlib.colors.Colormap
    """The color table of the images."""

    norm: matplotlib.colors.Normalize
    """The brightness of the images, the same in every frame."""

    label_colorbar: str
    """The label of the colorbar of the images."""

    def index(self, time: astropy.time.Time) -> int:
        """The index of the image whose exposure is centered closest to `time`."""
        return int(np.argmin(np.abs((self.time - time).to(u.s))))


def _field() -> tuple[tuple[float, float], tuple[float, float]]:
    """
    The helioprojective :math:`x` and :math:`y` limits, in arcseconds, of
    every panel, those of the DEM movie.
    """
    return esis_jet_paper.figures._dem_movie._field()


def _inside(position: na.AbstractCartesian2dVectorArray) -> na.AbstractScalar:
    """Whether the center of each pixel lies inside the field of :func:`_field`."""
    (x_min, x_max), (y_min, y_max) = _field()
    center = position.to(u.arcsec).cell_centers(axis=_axis)
    result = (center.x > x_min * u.arcsec) & (center.x < x_max * u.arcsec)
    return result & (center.y > y_min * u.arcsec) & (center.y < y_max * u.arcsec)


def _crop(position: na.AbstractCartesian2dVectorArray) -> dict[str, slice]:
    """
    The pixels whose centers lie inside the field of :func:`_field` in any
    image, and one more on every side.
    """
    inside = _inside(position)
    result = {}
    for axis in _axis:
        others = tuple(i for i, a in enumerate(inside.axes) if a != axis)
        index = np.flatnonzero(np.any(inside.ndarray, axis=others))
        result[axis] = slice(max(int(index[0]) - 1, 0), int(index[-1]) + 2)
    return result


def _norm(
    position: na.AbstractCartesian2dVectorArray,
    intensity: na.AbstractScalar,
) -> matplotlib.colors.LogNorm:
    """
    A logarithmic scale from the :data:`percentile_min` th to the
    percentile of the DEM movie of `intensity`, over the pixels whose centers
    lie inside the field of :func:`_field` in every image.
    """
    values = np.where(_inside(position), intensity, np.nan).ndarray
    percentile_max = esis_jet_paper.figures._dem_movie.percentile
    return matplotlib.colors.LogNorm(
        vmin=np.nanpercentile(values, percentile_min),
        vmax=np.nanpercentile(values, percentile_max),
        clip=True,
    )


def _panel_aia(images: sdo.aia.Filtergram, wavelength: int) -> _Panel:
    """The panel of the channel of `images` at `wavelength` angstroms, in DN per second."""
    channels = np.round(images.inputs.wavelength.ndarray.to_value(u.AA))
    images = images[{"channel": int(np.flatnonzero(channels == wavelength)[0])}]
    images = images[_crop(images.inputs.position)]
    position = images.inputs.position.to(u.arcsec)
    intensity = (images.outputs / images.timedelta).to(u.DN / u.s).value
    return _Panel(
        label=rf"AIA {wavelength}\,\AA",
        position=position,
        intensity=intensity,
        time=images.inputs.time.ndarray + images.timedelta.ndarray / 2,
        cmap=sunpy.visualization.colormaps.color_tables.aia_color_table(
            wavelength * u.AA
        ),
        norm=_norm(position, intensity),
        label_colorbar=r"DN\,s$^{-1}$",
    )


def _panel_xrt() -> _Panel:
    """The panel of XRT Al_poly, whose images are already in DN per second."""
    images = esis_jet_paper.xrt()
    images = images[_crop(images.inputs.position)]
    position = images.inputs.position.to(u.arcsec)
    intensity = images.outputs.to(u.DN / u.s).value
    return _Panel(
        label=r"XRT Al\_poly",
        position=position,
        intensity=intensity,
        time=images.inputs.time.ndarray + images.timedelta.ndarray / 2,
        cmap=sunpy.visualization.colormaps.color_tables.xrt_color_table(),
        norm=_norm(position, intensity),
        label_colorbar=r"DN\,s$^{-1}$",
    )


def _panel_hmi() -> _Panel:
    """The panel of the magnetograms of HMI, in gauss."""
    images = esis_jet_paper.hmi()
    images = images[_crop(images.inputs.position)]
    return _Panel(
        label="HMI",
        position=images.inputs.position.to(u.arcsec),
        intensity=images.outputs.to(u.G).value,
        time=images.inputs.time.ndarray + _cadence_hmi / 2,
        # The default of `sunpy` for the magnetograms of HMI, white where the
        # field points toward the observer.
        cmap="gray",
        norm=matplotlib.colors.Normalize(
            vmin=-limit.to_value(u.G),
            vmax=limit.to_value(u.G),
            clip=True,
        ),
        label_colorbar=r"$B_\mathrm{LOS}$ (G)",
    )


@functools.cache
def _panels() -> list[_Panel]:
    """
    The panels of the figure beside that of ESIS: the channels of AIA at 304,
    171, and 193 angstroms, XRT Al_poly, and the magnetograms of HMI.
    """
    return [
        _panel_aia(esis_jet_paper.aia_304(), 304),
        _panel_aia(esis_jet_paper.aia(), 171),
        _panel_aia(esis_jet_paper.aia(), 193),
        _panel_xrt(),
        _panel_hmi(),
    ]


def frames() -> astropy.time.Time:
    """The time of each frame of the movie: the middle of each exposure of AIA 304 Å."""
    return _panels()[0].time


def _draw(ax: plt.Axes, panel: _Panel, time: astropy.time.Time) -> astropy.time.Time:
    """
    Draw the image of `panel` whose exposure is centered closest to `time` on
    `ax`, in place of any drawn there before, and return the middle of its
    exposure.
    """
    for artist in list(ax.collections):
        artist.remove()
    index = panel.index(time)
    na.plt.pcolormesh(
        panel.position[{"time": index}],
        C=panel.intensity[{"time": index}],
        ax=ax,
        cmap=panel.cmap,
        norm=panel.norm,
        # in the PDF, so that no seams show between the pixels
        rasterized=True,
    )
    return panel.time[index]


def _draw_esis(ax: plt.Axes, time: astropy.time.Time) -> None:
    """
    Mark the panel of ESIS on `ax`, whose images are not ready yet, as to
    come during the exposures of ESIS and as empty outside of them.
    """
    for text in list(ax.texts):
        text.remove()
    ax.set_facecolor("0.92")
    during = (exposures_esis[0] <= time) & (time <= exposures_esis[1])
    ax.text(
        x=0.5,
        y=0.5,
        s="to come" if during else "no exposure",
        ha="center",
        va="center",
        transform=ax.transAxes,
        color="0.4",
    )


def _colorbar(fig: plt.Figure, panel: _Panel, ax: plt.Axes) -> None:
    """Add the colorbar of `panel` beside `ax`, with plain numbers on a logarithmic scale."""
    colorbar = fig.colorbar(
        matplotlib.cm.ScalarMappable(norm=panel.norm, cmap=panel.cmap),
        ax=ax,
        label=panel.label_colorbar,
    )
    if isinstance(panel.norm, matplotlib.colors.LogNorm):
        axis = colorbar.ax.yaxis
        # Enough ticks for a channel whose colors span less than a decade.
        axis.set_major_locator(matplotlib.ticker.LogLocator(subs=(1, 2, 3, 5)))
        axis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
        axis.set_minor_formatter(matplotlib.ticker.NullFormatter())


def _limits(ax: plt.Axes) -> None:
    """Set the limits of `ax` to the field of :func:`_field`, with square pixels."""
    xlim, ylim = _field()
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_aspect("equal")
    ax.set_xlabel("")
    ax.set_ylabel("")


def index_still() -> int:
    """The index of the frame shown in the PDF, the closest to the still of the DEM movie."""
    time_still = esis_jet_paper.figures._dem_movie.time_still
    return int(np.argmin(np.abs((frames() - time_still).to(u.s))))


def _frame() -> tuple[plt.Figure, Callable[[astropy.time.Time], None]]:
    """
    A figure laid out like a frame of the movie, and a function which draws
    on it the frame at a given time.
    """
    panels = _panels()
    fig, axs = plt.subplots(
        nrows=2,
        ncols=3,
        sharex=True,
        sharey=True,
        figsize=(aastex.text_width_inches, 0.55 * aastex.text_width_inches),
        constrained_layout=True,
    )
    axs = axs.ravel()
    # The channels of AIA along the top row, and ESIS, XRT, and HMI below.
    ax_esis = axs[3]
    axs_panels = [axs[0], axs[1], axs[2], axs[4], axs[5]]
    for ax, panel in zip(axs_panels, panels):
        _colorbar(fig, panel, ax)
    for ax in axs:
        _limits(ax)
    for ax in axs[3:]:
        ax.set_xlabel("$x$ (arcsec)")
    for ax in axs[::3]:
        ax.set_ylabel("$y$ (arcsec)")

    def draw(time: astropy.time.Time) -> None:
        _draw_esis(ax_esis, time)
        ax_esis.set_title(_label_esis)
        for ax, panel in zip(axs_panels, panels):
            middle = _draw(ax, panel, time)
            ax.set_title(f"{panel.label}, {middle.strftime('%H:%M:%S')}")
        fig.suptitle(f"2019 September 30, {time.strftime('%H:%M:%S')} UT")

    return fig, draw


@functools.cache
def _movie() -> pathlib.Path:
    """
    Write the movie, one frame for each image of AIA 304 Å, beside the image
    of each other instrument whose exposure is centered closest to it, and
    return its path.

    It is written once in each session, since it takes a while.
    """
    # The movie is drawn in the same fonts as the still, even when it is
    # made outside of :func:`esis_jet_paper.document`.
    with plt.rc_context(esis_jet_paper.rc):
        fig, draw = _frame()

        # Beside the PDF, where `aastex` would otherwise copy it.
        movie = pathlib.Path(esis_jet_paper.__file__).parent / _name_movie
        writer = matplotlib.animation.FFMpegWriter(
            fps=esis_jet_paper.figures._dem_movie.fps,
            codec="h264",
            extra_args=["-pix_fmt", "yuv420p"],
        )
        # Less than the DEM movie, so that the movie stays small enough for
        # the AAS journals, with still about two pixels of the screen for
        # each pixel of AIA.
        with writer.saving(fig, movie, dpi=_dpi_movie):
            # Constrained layout settles on the second draw of axes with a
            # fixed aspect, so draw once before the first frame is recorded,
            # then hold the layout, so that the panels do not shift as the
            # times in their titles change.
            draw(frames()[0])
            fig.canvas.draw()
            fig.set_layout_engine("none")
            for time in frames():
                draw(time)
                writer.grab_frame()
        plt.close(fig)

    return movie


def time_series() -> aastex.FigureStar:
    """
    Event E in ESIS O V, AIA 304, 171, and 193 Å, XRT Al_poly, and the
    magnetograms of HMI, at one time in the PDF and at every image of AIA
    304 Å from 18:00 to 18:20 UT in the movie.
    """
    movie = _movie()

    with plt.rc_context(esis_jet_paper.rc):
        fig, draw = _frame()
        draw(frames()[index_still()])

    result = aastex.FigureStar(
        "fig:timeSeries",
        position="t",
        animation=aastex.Animation(movie, url=esis_jet_paper.url(movie.name)),
    )
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
Event E in \ESIS\ \OV, in \AIA\ \SIlist{304;171;193}{\angstrom}, in \XRT\ Al\_poly, and in the
\LOSShort\ magnetograms of \HMI\ at \timeSeriesStill~UT, close to the time of the still of
Figure~\ref{fig:demMovie}, over its field.
Each panel shows the image of its instrument whose exposure is centered closest to that time,
on its own pixels, and is labeled with the middle of that exposure.
The brightness of each channel is on a logarithmic scale between percentiles
\timeSeriesPercentileMin\ and \demMoviePercentile\ of its intensity over the field in every
frame of the animation, and the magnetograms saturate at $\pm$\timeSeriesLimit, white where the
field points toward the observer and black where it points away.
The animation shows each of the \timeSeriesFrames\ images of \AIA\ \SI{304}{\angstrom} from
\timeSeriesStart\ to \timeSeriesStop~UT, beside the image of each other instrument closest to
it in time, at \demMovieFps\ frames per second, and runs for \timeSeriesDuration.
The panel of \ESIS\ is empty outside of its exposures, from \esisStart\ to \esisStop~UT.
\roy{The \ESIS\ \OV\ images are left out until the \ESIS\ data are ready.}
"""))
    return result
