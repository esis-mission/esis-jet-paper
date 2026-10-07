import aastex

__all__ = [
    "temperature",
]


def temperature() -> aastex.Section:
    result = aastex.Section("Temperature")
    result.append(r"""
\begin{outline}
\item \textbf{Data.}
    \AIA\ \EUV\ intensities \citep{Lemen2012}, \XRT\ intensities \citep{Golub2007}, and the \ESIS\
    line intensities, co-aligned and averaged over the event and over a background region of
    network, at several times through the event.
\item \textbf{Temperature responses.}
    The \AIA\ and \XRT\ responses and the contribution functions of the \ESIS\ lines, all computed
    from CHIANTI \citep{DelZanna2021} with the same abundances and ionization equilibrium so that the
    instruments can be combined.
    The \ESIS\ lines of \OIII, \OIV, and \OV\ extend the coverage of \AIA\ and \XRT\ down into the
    \TR, and \MgX\ overlaps the coolest coronal channels of \AIA.
    \HeI\ and \AIA\ \SI{304}{\angstrom} are optically thick and are left out of the inversion.
\item \textbf{Radiometric calibration.}
    The \ESIS\ intensities are needed in absolute units here, unlike in
    Section~\ref{sec:SpectralInversionandDopplerShifts}; how the channels are cross-calibrated
    against \AIA\ and the uncertainty this contributes.
\item \textbf{\DEM\ inversion} \citep{Plowman2013,Plowman2020}, implemented in the \texttt{utu}
    package, cross-checked against an independent method \citep{Hannah2012,Cheung2015}.
    Report the \DEMs\ with and without each instrument, to show what each contributes.
\item \textbf{Results.}
    The \DEM\ of event E compared with that of its surroundings, its peak temperature
    (\temperaturePeak), and whether the event has a coronal component visible to \XRT\ or is
    confined to the \TR, the question raised by \citet{Teriaca2002}.
    Whether the temperature differs between the cusp and the footpoint of the inverted Y.
\item \textbf{Figures:} the temperature responses of the three instruments;
    the \DEMs\ of event E and of the background.
\end{outline}""")
    return result
