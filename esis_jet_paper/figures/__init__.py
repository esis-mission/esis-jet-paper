"""
The figures of this article, each a factory function returning an
:class:`aastex.Figure`.
"""

from ._backgrounds import backgrounds
from ._dem_backgrounds import dem_backgrounds
from ._dem_movie import dem_movie
from ._dem_regions import dem_regions
from ._light_curves import light_curves
from ._temperature_responses import temperature_responses

__all__ = [
    "backgrounds",
    "dem_backgrounds",
    "dem_movie",
    "dem_regions",
    "light_curves",
    "temperature_responses",
]
