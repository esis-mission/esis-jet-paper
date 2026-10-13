"""
The appearance shared by every figure in the article.
"""

__all__ = [
    "rc",
]

rc = {
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 9,
    "lines.linewidth": 1,
}
"""
The :mod:`matplotlib` settings every figure and movie is drawn with, so that
their text is set in the same font as the article.
"""
