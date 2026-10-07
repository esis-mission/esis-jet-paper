import aastex

__all__ = [
    "observations",
]


def observations() -> aastex.Section:
    result = aastex.Section("Observations")
    result.append(r"""
\begin{outline}
\item \textbf{The \ESIS\ flight} \citep{Parker2022}.
    Launched from White Sands Missile Range at 18:04~UT on 2019 September 30, with \SI{10}{\second}
    exposures from 18:06:11 to 18:11:01~UT.
    The octagonal \FOV, about $11.5'$ across, was pointed near disk center during an exceptionally quiet
    period, in which GOES had detected no flare of B~class or above since 2019 July 7.
    The passband and its lines: \HeI\ \SI{584}{\angstrom}, \OIII\ \SI{600}{\angstrom},
    \OIV\ \SIlist{608;610}{\angstrom}, \MgX\ \SIlist{610;625}{\angstrom}, and \OV\ \SI{630}{\angstrom},
    with the temperature at which each is formed.
\item \textbf{Coordinated observations.}
    \AIA\ \EUV\ images at a \SI{12}{\second} cadence \citep{Lemen2012};
    \HMI\ \LOSShort\ magnetograms at a \SI{45}{\second} cadence, about seven of which cover the
    flight \citep{Scherrer2012};
    \XRT\ images of a field near disk center at a cadence of about \SI{18}{\second} throughout the
    flight \citep{Golub2007,Kosugi2007}, \roy{filter(s) and field of view to confirm}.
    \IRISCapital\ ran coarse rasters near disk center during the launch window; check whether any
    of them crossed event E.
\item \textbf{Co-alignment.}
    \ESIS\ to \AIA\ \SI{304}{\angstrom} (which correlates best with \HeI), and \HMI\ and \XRT\ to
    \AIA, with the residual misalignment that bounds the comparisons in
    Sections~\ref{sec:MagneticTopology} and~\ref{sec:Temperature}.
\item \textbf{Overview of event E.}
    Its location, (\ang{;;47.8}, \ang{;;-87.8}), about \ang{;;100} from disk center, and its
    lifetime (\eventDuration), including the parts before and after the \ESIS\ exposures from \AIA.
    Its inverted-Y morphology in \OV\ and in the \AIA\ channels, an order of magnitude brighter than
    the surrounding network, and the northward drift of its blue-shifted side by about
    \ang{;;11} over four minutes.
\item \textbf{Phases of the event}, as seen in the preliminary inversions:
    (1) blue shifts of about \SI{60}{\kilo\meter\per\second} directly beside strong red shifts near
    the right footpoint of the inverted Y;
    (2) the blue-shifted component migrates to the cusp while the red-shifted component stays at the
    footpoint;
    (3) a blue-shifted blob moves along the right leg at an apparent speed of
    \SIrange{100}{200}{\kilo\meter\per\second} in the plane of the sky.
\item \textbf{Figures:} the full \ESIS\ field with event E boxed;
    a time series of event E in \ESIS\ \OV, \AIA\ \SIlist{304;171;193}{\angstrom}, \XRT, and \HMI.
\end{outline}""")
    return result
