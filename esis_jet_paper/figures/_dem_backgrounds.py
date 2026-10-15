import functools

import aastex
import astropy.units as u
import matplotlib.colors
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np
import utu

import esis_jet_paper

__all__ = [
    "dem_backgrounds",
    "inversions",
]

_scale = 1e27 / u.cm**5
"""The unit the DEM is shown in, the same as in the DEM movie."""


@functools.cache
def inversions() -> dict[int, tuple[na.FunctionArray, na.AbstractScalar]]:
    """
    The DEM and the chi squared inverted from each background of the still of
    the DEM movie, keyed by the width of the background.

    The uncertainty is that of the intensities observed, though the background
    averages hundreds of pixels, so that its DEM is as smooth over temperature
    as that of a single pixel.
    """
    observation, background = esis_jet_paper.figures._backgrounds._still()
    response = esis_jet_paper.temperature_response()
    return {
        size: utu.dem.plowman(
            intensity=intensity,
            uncertainty=observation.uncertainty,
            response=response,
            axis_channel="channel",
            axis_temperature="temperature",
        )
        for size, intensity in background.items()
    }


def dem_backgrounds() -> aastex.FigureStar:
    """
    The DEM of event E at the time of the still of the DEM movie and the DEMs
    of its backgrounds, as false-color images and at each of
    :data:`esis_jet_paper.points`.
    """
    module = esis_jet_paper.figures._dem_movie
    index = module.index_still()
    observation, _ = esis_jet_paper.figures._backgrounds._still()
    nearest = esis_jet_paper.figures._backgrounds._nearest(observation)
    position = observation.position.to(u.arcsec)
    xlim, ylim = module._field()

    observed = esis_jet_paper.dem().dem.outputs[{"time": index}]
    dems = {"observed": observed}
    for size, (dem, _) in inversions().items():
        dems[rf"background ${size} \times {size}$"] = dem.outputs
    dems = {
        label: (dem / _scale).to(u.dimensionless_unscaled)
        for label, dem in dems.items()
    }
    linestyles = ["-", "--", ":"]

    logt = np.log10(esis_jet_paper.temperature_response().inputs / u.K)
    where = logt >= module.temperature_min - 1e-6
    where = where & (logt <= module.temperature_max + 1e-6)
    temperature = {"temperature": np.flatnonzero(where.ndarray)}
    # The brightness scale of the top row of the DEM movie.
    vmax = module._row(False).vmax

    fig, axs = plt.subplots(
        nrows=2,
        ncols=3,
        figsize=(aastex.text_width_inches, 0.75 * aastex.text_width_inches),
        constrained_layout=True,
    )
    for ax, (label, dem) in zip(axs[0], dems.items()):
        na.plt.rgbmesh(
            logt[temperature],
            position,
            C=dem[temperature],
            axis_wavelength="temperature",
            ax=ax,
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
            ax=ax,
            cmap=matplotlib.colors.ListedColormap(["white"]),
            rasterized=True,
        )
        esis_jet_paper.figures._backgrounds._points(ax, "white")
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_aspect("equal")
        ax.set_title(label)
        ax.set_xlabel("$x$ (arcsec)")
        ax.set_ylabel("")
    axs[0, 0].set_ylabel("$y$ (arcsec)")

    peak = max(
        float(np.nanmax(dem[i].ndarray))
        for dem in dems.values()
        for i in nearest.values()
    )
    for ax, (name, i) in zip(axs[1], nearest.items()):
        # The range of temperatures colored in the images.
        ax.axvspan(
            module.temperature_min, module.temperature_max, color="0.9", linewidth=0
        )
        for (label, dem), linestyle in zip(dems.items(), linestyles):
            na.plt.plot(
                logt,
                dem[i],
                axis="temperature",
                ax=ax,
                color="black",
                linestyle=linestyle,
                label=label,
            )
        ax.set_yscale("log")
        # Three decades, as in the DEM movie.
        ax.set_ylim(peak / 1e3, 2 * peak)
        ax.set_xlim(float(logt.min().ndarray), float(logt.max().ndarray))
        ax.set_title(name)
        ax.set_xlabel(r"$\log_{10} T$")
        ax.set_ylabel("")
    axs[1, 0].set_ylabel(r"DEM ($10^{27}\,\mathrm{cm^{-5}}$)")
    handles, labels = axs[1, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncols=3)

    result = aastex.FigureStar("fig:demBackgrounds", position="t")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
The \DEM\ of event E at \demMovieStill~UT, as in the top row of Figure~\ref{fig:demMovie} (left),
and the \DEMs\ inverted from its backgrounds of \demBackgroundSize\ by \demBackgroundSize\
(middle) and \backgroundsSizeWide\ by \backgroundsSizeWide\ pixels (right) in
Figure~\ref{fig:backgrounds}, as false-color images
colored as in Figure~\ref{fig:demMovie}, on the brightness scale of its top row (top), and in the
pixel nearest each of the three circled points (bottom), with the temperatures colored in the
images shaded gray.
White pixels are those where \XRT\ saturated, which have no \DEM.
"""))
    return result
