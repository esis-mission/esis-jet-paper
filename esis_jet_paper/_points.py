__all__ = [
    "linestyles",
    "points",
]

points = {
    "base": (49, -86),
    "footpoint": (68, 0),
}
"""
The helioprojective coordinates, in arcseconds, of the two points of event E
which the figures follow: its base and its northern footpoint.
"""

linestyles = {
    "base": "-",
    "footpoint": "--",
}
"""The style of the line of each of :data:`points`, the same in every figure."""
