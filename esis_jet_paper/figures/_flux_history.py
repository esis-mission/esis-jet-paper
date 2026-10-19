import functools

import aastex
import astropy.coordinates
import astropy.time
import astropy.units as u
import matplotlib.cm
import matplotlib.colors
import matplotlib.dates
import matplotlib.patches
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np
import sunpy.coordinates
import sunpy.sun.constants

import esis_jet_paper

__all__ = [
    "flux_history",
    "history",
    "index_still",
    "limit",
    "noise",
    "radii",
    "threshold",
]

_axis = ("detector_x", "detector_y")
"""The axes along which the pixels of every magnetogram are arranged."""

radii = {
    "base": 30 * u.arcsec,
    "footpoint": 10 * u.arcsec,
}
"""
The radius of the circle about the base and about the northern footpoint of
event E within which the flux is summed.

The circle about the base is wider, so that the patches of negative polarity
beside it stay inside it as they move over the day. In a narrower one the
negative flux falls before event E only because they move out of it: by
about a third over the day within 20 arcseconds, but by less than a tenth
within 30.
"""

threshold = 3
"""
The multiple of the :func:`noise` of its magnetogram by which the field of a
pixel must be stronger for the pixel to count toward the flux.
"""

limit = 100 * u.G
"""The field at which the colors of the magnetogram saturate."""

_width_bin = 0.1 * u.G
"""The width of the bins of the histogram from which :func:`noise` is measured."""

_range_noise = 20 * u.G
"""How far from zero the histogram from which :func:`noise` is measured reaches."""

_cmap = matplotlib.colormaps["RdBu_r"]
"""The colors of the magnetogram, red where the field points toward the observer."""

_colors = {
    "positive": matplotlib.colors.to_hex(_cmap(0.85)),
    "negative": matplotlib.colors.to_hex(_cmap(0.15)),
}
"""The color of the line of each polarity, that of its side of :data:`_cmap`."""


@functools.cache
def noise() -> na.AbstractScalar:
    """
    The noise of each magnetogram of :func:`esis_jet_paper.hmi_history`: the
    standard deviation of the normal distribution whose full width at half
    maximum is that of the core of the histogram of its field.

    Most pixels of the quiet Sun hold little more than noise, so the core of
    the histogram is the noise, while the network fills its wings, which the
    standard deviation of every pixel would count.
    """
    field = esis_jet_paper.hmi_history().outputs
    histogram = na.histogram(
        field,
        bins={"field": int(2 * _range_noise / _width_bin)},
        axis=_axis,
        min=-_range_noise,
        max=_range_noise,
    ).outputs
    above = histogram > np.max(histogram, axis="field") / 2
    width = above.sum("field") * _width_bin
    return width / (2 * np.sqrt(2 * np.log(2)))


@functools.cache
def _centers() -> dict[str, na.Cartesian2dVectorArray]:
    """
    The center of each circle of :data:`radii` at the time of each magnetogram
    of :func:`esis_jet_paper.hmi_history`, in helioprojective coordinates.

    Each of :data:`esis_jet_paper.points` is where it is at the still of the
    DEM movie, and is carried from there by the rotation of the Sun.
    SDO and Hinode both orbit the Earth, so each is seen from the Earth.
    """
    time_still = esis_jet_paper.figures._dem_movie.time_still
    time = astropy.time.Time(esis_jet_paper.hmi_history().inputs.time.ndarray)
    frame_still = sunpy.coordinates.Helioprojective(
        observer=sunpy.coordinates.get_earth(time_still),
        obstime=time_still,
    )
    frame = sunpy.coordinates.Helioprojective(
        observer=sunpy.coordinates.get_earth(time),
        obstime=time,
    )
    result = {}
    for name in radii:
        x, y = esis_jet_paper.points[name]
        point = astropy.coordinates.SkyCoord(
            x * u.arcsec, y * u.arcsec, frame=frame_still
        )
        with sunpy.coordinates.propagate_with_solar_surface():
            point = point.transform_to(frame)
        result[name] = na.Cartesian2dVectorArray(
            x=na.ScalarArray(point.Tx.to(u.arcsec), "time"),
            y=na.ScalarArray(point.Ty.to(u.arcsec), "time"),
        )
    return result


@functools.cache
def history() -> dict[str, dict[str, na.AbstractScalar]]:
    """
    The positive and the negative magnetic flux within each circle of
    :data:`radii` in each magnetogram of :func:`esis_jet_paper.hmi_history`,
    keyed by the name of the point and then by ``"positive"`` or
    ``"negative"``, each as a magnitude.

    Only the pixels whose field is stronger than :data:`threshold` times the
    :func:`noise` of their magnetogram count.
    The field is taken to be vertical, so each pixel holds the field along
    the line of sight over :math:`\\mu`, the cosine of the angle between the
    line of sight and the vertical, through its area on the sky over
    :math:`\\mu`.
    """
    images = esis_jet_paper.hmi_history()
    field = images.outputs
    pixel = images.inputs.position.cell_centers(axis=_axis)

    # The distance from the observer to the surface along the line of sight
    # of each pixel, at which its angular size is taken.
    time = astropy.time.Time(images.inputs.time.ndarray)
    distance = na.ScalarArray(sunpy.coordinates.get_earth(time).radius, "time")
    radius = sunpy.sun.constants.radius
    angle = np.arccos(np.cos(pixel.x) * np.cos(pixel.y))
    mu = np.sqrt(1 - np.square(distance * np.sin(angle) / radius))
    depth = distance * np.cos(angle) - radius * mu

    cdelt = images.inputs.cdelt.position
    area = np.square(depth) * cdelt.x.to_value(u.rad) * cdelt.y.to_value(u.rad)
    flux = (field * area / np.square(mu)).to(u.Mx)

    strong = np.abs(field) > threshold * noise()
    result = {}
    for name, center in _centers().items():
        offset = np.sqrt(np.square(pixel.x - center.x) + np.square(pixel.y - center.y))
        inside = strong & (offset <= radii[name])
        result[name] = {
            "positive": np.where(inside & (field > 0), flux, 0).sum(_axis),
            "negative": -np.where(inside & (field < 0), flux, 0).sum(_axis),
        }
    return result


def index_still() -> int:
    """The index of the magnetogram closest to the still of the DEM movie."""
    time = esis_jet_paper.hmi_history().inputs.time.ndarray
    time_still = esis_jet_paper.figures._dem_movie.time_still
    return int(np.argmin(np.abs((time - time_still).to(u.s))))


def flux_history() -> aastex.FigureStar:
    """
    The magnetogram of HMI closest to the still of the DEM movie, with the
    circles of :data:`radii` drawn on it, beside the positive and the negative
    flux within each circle over the day before event E.
    """
    images = esis_jet_paper.hmi_history()
    index = index_still()
    image = images[{"time": index}]
    time = images.inputs.time
    time = na.ScalarArray(time.ndarray.datetime64, axes=time.axes)
    flux = history()
    start, stop = esis_jet_paper.figures._light_curves.lifetime()

    fig = plt.figure(
        figsize=(aastex.text_width_inches, 0.42 * aastex.text_width_inches),
        constrained_layout=True,
    )
    grid = fig.add_gridspec(nrows=len(radii), ncols=2, width_ratios=[1, 1.3])
    ax_image = fig.add_subplot(grid[:, 0])
    axs = [fig.add_subplot(grid[0, 1])]
    axs += [fig.add_subplot(grid[r, 1], sharex=axs[0]) for r in range(1, len(radii))]

    norm = matplotlib.colors.Normalize(-limit.value, limit.value)
    na.plt.pcolormesh(
        image.inputs.position.to(u.arcsec),
        C=image.outputs.to_value(limit.unit),
        ax=ax_image,
        cmap=_cmap,
        norm=norm,
        # in the PDF, so that no seams show between the pixels
        rasterized=True,
    )
    for name, center in _centers().items():
        center = center[{"time": index}]
        x = float(center.x.ndarray.to_value(u.arcsec))
        y = float(center.y.ndarray.to_value(u.arcsec))
        radius = radii[name].to_value(u.arcsec)
        circle = matplotlib.patches.Circle(
            (x, y),
            radius=radius,
            fill=False,
            edgecolor="black",
            linestyle=esis_jet_paper.linestyles[name],
        )
        ax_image.add_patch(circle)
        ax_image.annotate(
            name,
            xy=(x, y + radius),
            xytext=(0, 2),
            textcoords="offset points",
            ha="center",
            va="bottom",
        )
    ax_image.set_aspect("equal")
    ax_image.set_title(f"{image.inputs.time.ndarray.strftime('%H:%M:%S')} UT")
    ax_image.set_xlabel("helioprojective $x$ (arcsec)")
    ax_image.set_ylabel("helioprojective $y$ (arcsec)")
    fig.colorbar(
        matplotlib.cm.ScalarMappable(norm=norm, cmap=_cmap),
        ax=ax_image,
        label=r"$B_\mathrm{LOS}$ (G)",
    )

    for ax, name in zip(axs, radii):
        for polarity, color in _colors.items():
            na.plt.plot(
                time,
                (flux[name][polarity] / (1e18 * u.Mx)).to(u.dimensionless_unscaled),
                axis="time",
                ax=ax,
                color=color,
                linestyle=esis_jet_paper.linestyles[name],
                label=polarity,
            )
        # The lifetime of event E, beneath the curves.
        ax.axvspan(start.datetime64, stop.datetime64, color="0.8", linewidth=0)
        ax.set_title(name)
        ax.set_ylim(bottom=0)
        ax.set_ylabel(r"flux ($10^{18}$ Mx)")
    for ax in axs[:-1]:
        ax.tick_params(labelbottom=False)
    axs[0].legend(loc="center left")
    axs[-1].set_xlabel("time (UT), 2019 September 29 to 30")
    axs[-1].set_xlim(time.ndarray.min(), time.ndarray.max())
    axs[-1].xaxis.set_major_locator(matplotlib.dates.HourLocator(byhour=[0, 6, 12, 18]))
    axs[-1].xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M"))

    result = aastex.FigureStar("fig:fluxHistory", position="t")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
The magnetic field beneath event E.
Left: the \LOSShort\ field of \HMI\ at \fluxHistoryStill~UT, in the magnetogram closest to the
still of Figure~\ref{fig:demMovie}, red where it points toward the observer and blue where it
points away, saturating at \fluxLimit.
The base of event E is circled with a radius of \fluxRadiusBase\ (solid), wide enough that the
patches of negative polarity beside it stay inside it as they move over the day, and its
northern footpoint with a radius of
\fluxRadiusFootpoint\ (dashed).
Right: the positive (red) and the negative (blue) magnetic flux within each circle in every
magnetogram from \fluxHistoryStart\ to \fluxHistoryStop, \fluxHistoryCadence\ apart, with each
circle carried along by the rotation of the Sun.
Only the pixels whose field is stronger than \fluxThreshold\ times the noise of their magnetogram,
about \fluxNoise, are counted, the noise being the width of the core of the histogram of the
field, and the field is taken to be vertical.
The gray band marks the lifetime of event E, from \eventStart\ to \eventStop~UT.
"""))
    return result
