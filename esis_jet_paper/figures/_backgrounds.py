import functools

import aastex
import astropy.units as u
import matplotlib.cm
import matplotlib.colors
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np

import esis_jet_paper

__all__ = [
    "backgrounds",
    "size_wide",
]

size_wide = 61
"""
The width, in pixels of XRT, of the background compared with that which
:func:`esis_jet_paper.dem` subtracts, about twice as wide.
"""

_limit_residual = 0.3
"""
The largest intensity left after a background is subtracted that is shown,
in the units each channel is scaled to.
"""

_axis = ("detector_x", "detector_y")
"""The axes along which the pixels of every image are arranged."""


def _sizes() -> tuple[int, int]:
    """
    The widths of the two backgrounds compared, that which
    :func:`esis_jet_paper.dem` subtracts and :data:`size_wide`.
    """
    return esis_jet_paper._dem._size_background, size_wide


@functools.cache
def _still() -> tuple["esis_jet_paper._dem._Observation", dict[int, na.AbstractScalar]]:
    """
    The intensities at the time of the still of the DEM movie, and their
    background for each of :func:`_sizes`, keyed by the size.
    """
    index = esis_jet_paper.figures._dem_movie.index_still()
    observation = esis_jet_paper._dem._observe(index)
    background = {
        size: esis_jet_paper._dem._background(observation, size) for size in _sizes()
    }
    return observation, background


def _nearest(
    observation: "esis_jet_paper._dem._Observation",
) -> dict[str, dict[str, na.AbstractScalar]]:
    """
    The index of the pixel of `observation` nearest each of
    :data:`esis_jet_paper.points`, keyed by the name of the point.
    """
    center = observation.position.cell_centers(axis=_axis)
    result = {}
    for name, (x, y) in esis_jet_paper.points.items():
        distance = np.square(center.x - x * u.arcsec)
        distance = distance + np.square(center.y - y * u.arcsec)
        result[name] = np.argmin(distance, axis=_axis)
    return result


def _points(ax: plt.Axes, color: str) -> None:
    """Circle each of :data:`esis_jet_paper.points` on `ax`."""
    for x, y in esis_jet_paper.points.values():
        ax.plot(
            x,
            y,
            marker="o",
            markersize=3,
            markeredgewidth=0.6,
            markerfacecolor="none",
            markeredgecolor=color,
        )


def backgrounds() -> aastex.FigureStar:
    """
    The intensity of each channel at the time of the still of the DEM movie,
    its backgrounds of each of :func:`_sizes`, and what is left when each is
    subtracted.
    """
    observation, background = _still()
    position = observation.position.to(u.arcsec)
    xlim, ylim = esis_jet_paper.figures._dem_movie._field()
    percentile = esis_jet_paper.figures._dem_movie.percentile

    wavelength = esis_jet_paper.channels.ndarray
    titles = [rf"{w.to_value(u.AA):.0f}\,\AA" for w in wavelength] + ["XRT"]
    rows = ["observed"]
    rows += [rf"${s} \times {s}$" for s in _sizes()]
    rows += [rf"observed $-$" "\n" rf"${s} \times {s}$" for s in _sizes()]

    cmap = "inferno"
    norm = matplotlib.colors.Normalize(0, 1)
    cmap_residual = "RdBu_r"
    norm_residual = matplotlib.colors.Normalize(-_limit_residual, _limit_residual)

    fig, axs = plt.subplots(
        nrows=len(rows),
        ncols=len(titles),
        sharex=True,
        sharey=True,
        figsize=(aastex.text_width_inches, 0.7 * aastex.text_width_inches),
        constrained_layout=True,
    )
    for c, title in enumerate(titles):
        channel = {"channel": c}
        observed = observation.intensity[channel]
        scale = np.nanpercentile(observed.ndarray, percentile)
        images = [observed] + [background[s][channel] for s in _sizes()]
        images = [(image / scale).to(u.dimensionless_unscaled) for image in images]
        residuals = [images[0] - image for image in images[1:]]
        for r, image in enumerate(images + residuals):
            ax = axs[r, c]
            residual = r >= len(images)
            na.plt.pcolormesh(
                position,
                C=image,
                ax=ax,
                cmap=cmap_residual if residual else cmap,
                norm=norm_residual if residual else norm,
                # in the PDF, so that no seams show between the pixels
                rasterized=True,
            )
            _points(ax, "black" if residual else "white")
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
            ax.set_aspect("equal")
            ax.set_xlabel("")
            ax.set_ylabel("")
        axs[0, c].set_title(title)
        axs[-1, c].set_xlabel("$x$ (arcsec)")
    for r, row in enumerate(rows):
        axs[r, 0].set_ylabel(f"{row}\n$y$ (arcsec)")

    fig.colorbar(
        matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap),
        ax=axs[:3],
        label="scaled intensity",
    )
    fig.colorbar(
        matplotlib.cm.ScalarMappable(norm=norm_residual, cmap=cmap_residual),
        ax=axs[3:],
        label="scaled intensity",
    )

    result = aastex.FigureStar("fig:backgrounds", position="t")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
The intensities of event E at \demMovieStill~UT, the time of the still of
Figure~\ref{fig:demMovie}, in each \EUV\ channel of \AIA, labeled by its wavelength, and in
\XRT\ Al\_poly (top row), on the pixels of \XRT\ from which the \DEM\ is inverted.
Beneath them are two backgrounds, the mean of the \demBackgroundSize\ by \demBackgroundSize\
pixels (\demBackgroundWidth) around each pixel, which the bottom row of
Figure~\ref{fig:demMovie} subtracts, and that of the \backgroundsSizeWide\ by
\backgroundsSizeWide\ pixels (\backgroundsWidthWide) around it, each without the brightest and
the faintest \demBackgroundProportion\ of them, and beneath those, what is left when each is
subtracted (bottom two rows, red where the intensity is above the background and blue where it
is below).
Each channel is scaled to the \demMoviePercentile th percentile of the intensity observed in it.
The base of event E, the hottest part of its spire, and its northern footpoint are circled.
"""))
    return result
