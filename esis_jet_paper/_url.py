import os

__all__ = [
    "url",
]

_url_default = "https://esis-mission.github.io/esis-jet-paper/"


def url(name: str = "") -> str:
    """
    Where a file built with this article is published, such as the movie of
    an animated figure.

    The ``pdf`` workflow publishes the article built from ``main`` at the root
    of the GitHub Pages site of this repository, and the article built from a
    pull request under ``pr/<number>/``.
    The ``tests`` workflow, which builds the article, says which of these a
    build is with the ``ESIS_JET_PAPER_URL`` environment variable.
    Anywhere else, such as a local build, the site of ``main`` is assumed.

    Movies are linked from the captions of their figures by passing this to
    :class:`aastex.Animation`, since no PDF reader can play them.

    Parameters
    ----------
    name
        The name of the published file, such as ``"event-e.mp4"``.
    """
    base = os.environ.get("ESIS_JET_PAPER_URL") or _url_default
    return base.rstrip("/") + "/" + name
