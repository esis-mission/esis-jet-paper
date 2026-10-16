import functools

import aastex
import astropy.time
import astropy.units as u
import hinode
import matplotlib.dates
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np
import sdo

import esis_jet_paper

__all__ = [
    "duration_quiet",
    "fraction_lifetime",
    "lifetime",
    "light_curves",
]

_axis = ("detector_x", "detector_y")
"""The axes along which the pixels of every image are arranged."""

_label_esis = r"ESIS O\,\textsc{v}, to come"
"""The label of the line of ESIS, whose data are not ready yet."""

fraction_lifetime = 0.1
"""
The fraction of its peak, above its level before the event, by which the base
of event E is brighter in AIA 304 angstroms than before the event for as long
as the event is taken to last.
"""

duration_quiet = 2 * u.min
"""
How long the light curves run, from their start, before event E begins: the
time over which the level of the base before the event is taken.
"""


def _middle(images: sdo.aia.Filtergram | hinode.xrt.Filtergram) -> na.ScalarArray:
    """The middle of each exposure of `images`, as :class:`numpy.datetime64`."""
    time = images.inputs.time
    middle = time.ndarray + images.timedelta.ndarray / 2
    return na.ScalarArray(middle.datetime64, axes=time.axes)


def _curves(
    position: na.AbstractCartesian2dVectorArray,
    intensity: na.AbstractScalar,
    saturated: None | na.AbstractScalar = None,
) -> tuple[dict[str, na.AbstractScalar], na.AbstractScalar]:
    """
    The mean intensity within :data:`esis_jet_paper.radii` of each of
    :data:`esis_jet_paper.points`, and the median intensity of each image.

    Parameters
    ----------
    position
        The helioprojective coordinates of the vertices of the pixels.
    intensity
        The intensity of each pixel.
    saturated
        Whether each pixel saturated.
        The mean of a region with a saturated pixel is only a lower limit, so
        it is NaN instead.
        If :obj:`None` (the default), no pixel saturated.
    """
    center = position.to(u.arcsec).cell_centers(axis=_axis)
    curves = {}
    for name, (x, y) in esis_jet_paper.points.items():
        distance = np.square(center.x - x * u.arcsec)
        distance = np.sqrt(distance + np.square(center.y - y * u.arcsec))
        inside = distance <= esis_jet_paper.radii[name]
        mean = np.where(inside, intensity, 0).sum(_axis) / inside.sum(_axis)
        if saturated is not None:
            mean = np.where(np.any(inside & saturated, axis=_axis), np.nan, mean)
        curves[name] = mean
    return curves, np.median(intensity, axis=_axis)


@functools.cache
def _channels() -> list[
    tuple[
        str,
        str,
        na.ScalarArray,
        dict[str, na.AbstractScalar],
        na.AbstractScalar,
    ]
]:
    """
    The label and the color of each channel, the middle of each exposure, the
    curves of :func:`_curves` in DN per second per pixel, and the median, for
    each EUV channel of AIA in order of wavelength and then for XRT.
    """
    result = []
    for images in [esis_jet_paper.aia(), esis_jet_paper.aia_304()]:
        for c in range(images.outputs.shape["channel"]):
            image = images[{"channel": c}]
            wavelength = image.inputs.wavelength.ndarray.to(u.AA).value
            curves, median = _curves(
                position=image.inputs.position,
                intensity=image.outputs / image.timedelta,
            )
            label = rf"{wavelength:.0f}\,\AA"
            color = esis_jet_paper.color_aia(wavelength * u.AA)
            channel = (label, color, _middle(image), curves, median)
            result.append((wavelength, channel))
    result = [channel for _, channel in sorted(result, key=lambda c: c[0])]

    images = esis_jet_paper.xrt()
    curves, median = _curves(
        position=images.inputs.position,
        intensity=images.outputs,
        saturated=images.saturated,
    )
    result.append(("XRT", esis_jet_paper.color_xrt, _middle(images), curves, median))

    return result


def window() -> tuple[astropy.time.Time, astropy.time.Time]:
    """The middles of the first and the last exposure of any channel."""
    times = [time.ndarray for _, _, time, _, _ in _channels()]
    start = min(t.min() for t in times)
    stop = max(t.max() for t in times)
    return astropy.time.Time(start), astropy.time.Time(stop)


@functools.cache
def lifetime() -> tuple[astropy.time.Time, astropy.time.Time]:
    """
    The middles of the first and the last exposure of the run of exposures of
    AIA 304 angstroms around the peak of the base of event E in which the base
    is brighter than its level before the event by more than
    :data:`fraction_lifetime` of its peak above that level.

    The brightness is that of the light curve of the base, over the median of
    its image, and its level before the event is the median over the first
    :data:`duration_quiet` of the light curve.
    AIA 304 angstroms is the channel in which the base brightens first.
    """
    images = esis_jet_paper.aia_304()[{"channel": 0}]
    curves, median = _curves(
        position=images.inputs.position,
        intensity=images.outputs / images.timedelta,
    )
    curve = (curves["base"] / median).to(u.dimensionless_unscaled)
    time = _middle(images)
    num = time.shape["time"]

    elapsed = time - time[{"time": 0}]
    quiet = elapsed < np.timedelta64(int(duration_quiet.to_value(u.s)), "s")
    level = np.nanmedian(np.where(quiet, curve, np.nan), axis="time")

    index = np.argmax(curve, axis="time")["time"]
    peak = curve[{"time": index}]
    above = curve > level + fraction_lifetime * (peak - level)

    i = na.arange(0, num, axis="time")
    first = np.where(~above & (i < index), i, -1).max() + 1
    last = np.where(~above & (i > index), i, num).min() - 1
    if first == 0 or last == num - 1:
        raise ValueError("Event E outlasts the light curves.")

    return (
        astropy.time.Time(time[{"time": first}].ndarray),
        astropy.time.Time(time[{"time": last}].ndarray),
    )


def light_curves() -> aastex.Figure:
    """
    The light curves of the base, the spire, and the northern footpoint of
    event E in every EUV channel of AIA and in XRT, each over the median of its image,
    with a line kept for ESIS.
    """
    channels = _channels()
    start, stop = window()

    names = list(esis_jet_paper.points)
    fig, axs = plt.subplots(
        nrows=len(names),
        sharex=True,
        figsize=(aastex.column_width_inches, 1.7 * aastex.column_width_inches),
        constrained_layout=True,
    )

    for ax, name in zip(axs, names):
        for label, color, time, curves, median in channels:
            na.plt.plot(
                time,
                (curves[name] / median).to(u.dimensionless_unscaled),
                axis="time",
                ax=ax,
                color=color,
                label=label,
            )
        # Kept for the O V intensity of ESIS, whose data are not ready yet.
        ax.plot([], [], color=esis_jet_paper.color_esis, label=_label_esis)
        # The lifetime of event E, beneath the curves.
        for time in lifetime():
            ax.axvline(time.datetime64, color="0.6", linestyle=":", zorder=1.5)
        ax.set_title(name)
        ax.set_ylim(bottom=0)
        ax.set_ylabel("intensity over median")

    axs[-1].set_xlabel("time (UT)")
    axs[-1].set_xlim(start.datetime64, stop.datetime64)
    axs[-1].xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M"))
    fig.legend(
        *axs[0].get_legend_handles_labels(),
        loc="outside upper center",
        ncols=3,
    )

    result = aastex.Figure("fig:lightCurves", position="t")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
The light curves of the base of event E (top), the hottest part of its spire (middle), and
its northern footpoint (bottom), the three points circled in Figure~\ref{fig:demMovie}, in each
\EUV\ channel of \AIA, labeled by its wavelength, and in \XRT\ Al\_poly, at the middle of
every exposure from \lightCurvesStart\ to \lightCurvesStop~UT.
Each is the mean intensity of the pixels within \radiusPoint\ of the point, or within
\radiusSpire\ of the spire, which is narrower, over the median intensity of its image, so
that 1 is the median in every channel.
The curve of \XRT\ at the base has a gap where \XRT\ saturated.
The dotted lines mark the lifetime of event E, from \eventStart\ to \eventStop~UT, over which
the base is brighter in \AIA\ \SI{304}{\angstrom} than in the first \lifetimeQuiet\ of the
curve by more than \lifetimeFraction\ of its peak brightening.
\roy{The \ESIS\ \OV\ curves are left out until the \ESIS\ data are ready.}
"""))
    return result
