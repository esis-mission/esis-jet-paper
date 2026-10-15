import astropy.units as u
import numpy as np
import sunpy.coordinates

import esis_jet_paper

__all__ = [
    "length",
    "linestyles",
    "points",
    "radii",
]

points = {
    "base": (49, -86),
    "spire": (52, -51),
    "footpoint": (68, 0),
}
"""
The helioprojective coordinates, in arcseconds, of the three points of event E
which the figures follow: its base, the hottest part of its spire, and its
northern footpoint.

The spire is hottest here in the DEM with the background subtracted, from
18:07 to 18:09 UT, around the still of the DEM movie.
"""

radii = {
    "base": 3 * u.arcsec,
    "spire": 1.5 * u.arcsec,
    "footpoint": 3 * u.arcsec,
}
"""
The radius of the region about each of :data:`points` whose mean intensity the
figures use, the same for the base and the footpoint, and narrower for the
spire, which is only about 3 arcseconds wide.
"""

linestyles = {
    "base": "-",
    "spire": ":",
    "footpoint": "--",
}
"""The style of the line of each of :data:`points`, the same in every figure."""


def length() -> u.Quantity:
    """
    The length of event E: the distance in the plane of the sky from its base
    to its northern footpoint, where the fainter arc which continues its spire
    ends.

    The angle between the two :data:`points` is taken at the distance of the
    Sun from the Earth at the still of the DEM movie, since SDO and Hinode
    both orbit the Earth.
    """
    (x_base, y_base), (x_footpoint, y_footpoint) = (
        points["base"],
        points["footpoint"],
    )
    angle = np.hypot(x_footpoint - x_base, y_footpoint - y_base) * u.arcsec
    time = esis_jet_paper.figures._dem_movie.time_still
    distance = sunpy.coordinates.get_earth(time).radius
    return (angle.to_value(u.rad) * distance).to(u.Mm)
