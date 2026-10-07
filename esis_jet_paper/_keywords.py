import aastex

__all__ = [
    "keywords",
]


def keywords() -> aastex.Keywords:
    """
    The Unified Astronomy Thesaurus concepts describing this article.
    """
    return aastex.Keywords(
        [
            aastex.UAT("Solar transition region", 1532),
            aastex.UAT("Solar magnetic reconnection", 1504),
            aastex.UAT("Solar magnetic fields", 1503),
            aastex.UAT("Solar extreme ultraviolet emission", 1493),
            aastex.UAT("Spectroscopy", 1558),
            aastex.UAT("Doppler shift", 401),
        ]
    )
