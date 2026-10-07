import aastex

__all__ = [
    "acronyms",
]


def acronyms() -> list[aastex.Acronym]:
    """
    A list of acronyms that are used in the body of the article.
    """
    return [
        aastex.Acronym("ESIS", "the EUV Snapshot Imaging Spectrograph"),
        aastex.Acronym("MOSES", "the Multi-Order Solar EUV Spectrograph"),
        aastex.Acronym("AIA", "the Atmospheric Imaging Assembly"),
        aastex.Acronym("HMI", "the Helioseismic and Magnetic Imager"),
        aastex.Acronym("XRT", "the X-Ray Telescope"),
        aastex.Acronym("IRIS", "the Interface Region Imaging Spectrograph"),
        aastex.Acronym("HRTS", "High Resolution Telescope and Spectrograph"),
        aastex.Acronym("EUV", "extreme ultraviolet"),
        aastex.Acronym("TR", "transition region"),
        aastex.Acronym("CTIS", "computed tomography imaging spectrograph", plural=True),
        aastex.Acronym("MART", "multiplicative algebraic reconstruction technique"),
        aastex.Acronym("FOV", "field of view"),
        aastex.Acronym("DEM", "differential emission measure", plural=True),
        aastex.Acronym("MCT", "magnetic charge topology"),
        aastex.Acronym("LOS", "line of sight", short=True),
    ]
