"""
The figures of this article, each a factory function returning an
:class:`aastex.Figure`.
"""

from ._dem_movie import dem_movie
from ._light_curves import light_curves

__all__ = [
    "dem_movie",
    "light_curves",
]
