import aastex

import esis_jet_paper

__all__ = [
    "background_subtraction",
]


def background_subtraction() -> aastex.Section:
    result = aastex.Section(
        "Background Subtraction",
        label="appendix:backgroundSubtraction",
    )
    result.append(r"""
\roy{For our collaborators, to compare two sizes of the background; probably to be removed
before submission.}
The bottom row of Figure~\ref{fig:demMovie} is inverted from the intensities of each pixel less
their background, the trimmed mean of the \demBackgroundSize\ by \demBackgroundSize\ pixels of
\XRT\ (\demBackgroundWidth) around it.
Figures~\ref{fig:backgrounds} and~\ref{fig:demBackgrounds} compare that background, at the time
of the still, with the trimmed mean of the \backgroundsSizeWide\ by \backgroundsSizeWide\ pixels
(\backgroundsWidthWide) around each pixel.
The wider background is smoother, and leaves more of the loops around event E behind when it is
subtracted.
Under the base of event E, either background is a small part of the intensity in every channel.
Under the spire, either is most of it, and its \DEM\ is close to that of the spire itself, so the
\DEM\ of the spire with the background subtracted is the one which depends the most on how the
background is chosen.
""")
    result.append(esis_jet_paper.figures.backgrounds())
    result.append(esis_jet_paper.figures.dem_backgrounds())
    return result
