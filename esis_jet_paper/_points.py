import astropy.units as u

__all__ = [
    "linestyles",
    "points",
    "radii",
]

points = {
    "base": (49, -86),
    "spire": (52, -66),
    "footpoint": (68, 0),
}
"""
The helioprojective coordinates, in arcseconds, of the three points of event E
which the figures follow: its base, the middle of its spire, and its northern
footpoint.
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
