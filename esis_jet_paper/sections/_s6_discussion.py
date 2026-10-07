import aastex

__all__ = [
    "discussion",
]


def discussion() -> aastex.Section:
    result = aastex.Section("Discussion")
    result.append(r"""
\begin{outline}
\item \textbf{A reconnection jet?}
    Bring together the flows, the topology, and the temperature into a single picture of event E,
    and ask whether it is consistent with reconnection at a null point or separator driving
    bidirectional outflows \citep{Innes1997,Pariat2009}.
\item \textbf{A minifilament eruption?}
    Compare the three phases of the event with the minifilament eruption picture
    \citep{Sterling2015,Sterling2016}: adjacent blue and red jets as the rising minifilament
    reconnects internally, the blue component moving to the cusp as it reconnects with the
    surrounding field, and the blob of the third phase as a plasmoid.
    Compare the size of the dome, the height of the null, and the speed and duration of the jet with
    the breakout model \citep{Wyper2017,Wyper2018}, and decide between standard and blowout
    \citep{Moore2010}.
\item \textbf{Energetics.}
    The kinetic and thermal energy of the event compared with the magnetic energy that the
    topology suggests was released.
\item \textbf{Context.}
    Where event E falls among \TR\ explosive events \citep{Brueckner1983,Dere1989}, network jets
    \citep{Tian2014,Chen2019}, and coronal jets \citep{Shibata1992,Raouafi2016}, and what it says
    about whether explosive events have a coronal counterpart \citep{Teriaca2002}.
\item \textbf{Snapshot spectroscopy.}
    What a slit raster would have recorded of the same event, and which conclusions depended on
    observing the whole event at once.
\end{outline}""")
    return result
