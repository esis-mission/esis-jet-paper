import aastex

__all__ = [
    "topology",
]


def topology() -> aastex.Section:
    result = aastex.Section("Magnetic Topology")
    result.append(r"""
\begin{outline}
\item \textbf{Magnetograms.}
    The \HMI\ \LOSShort\ magnetograms \citep{Scherrer2012} around the time of the flight, their
    co-alignment with \ESIS, and the evolution of the photospheric flux beneath event E over the
    preceding hours: is there a parasitic polarity at the footpoint of the inverted Y, and is it
    emerging or cancelling \citep{Panesar2016}?
\item \textbf{\MCTCapital} \citep{Longcope2002,Longcope2005}.
    Partition the magnetogram into unipolar sources, represent each as a point charge, and compute
    the potential field they produce \citep{Barnes2005}.
    Locate its null points, spines, separatrix surfaces, and separators, and in particular any
    fan-spine structure above the event and the height of its null.
\item \textbf{Separatrices and flows.}
    Overlay the separatrix footprints and the location of any null point or separator on the
    Doppler maps of Section~\ref{sec:SpectralInversionandDopplerShifts}.
    Test whether the blue and red components lie on opposite sides of a separatrix, whether the
    cusp of the inverted Y lies beneath the null, and whether the migration of the blue-shifted
    component to the cusp follows a separatrix.
\item \textbf{Energetics.}
    The flux transferred across the separator during the event, and the energy that its
    reconnection could release \citep{Longcope2001}.
\item \textbf{Robustness.}
    How the topology changes with the partitioning threshold and from one magnetogram to the next,
    and whether the features that matter to event E persist in the weak fields of the quiet Sun.
\item \textbf{Figures:} the magnetogram with its sources and separatrix footprints;
    the same footprints overlaid on the Doppler maps; a three-dimensional view of the separatrices
    and the null.
\end{outline}""")
    return result
