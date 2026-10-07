import aastex

__all__ = [
    "conclusions",
]


def conclusions() -> aastex.Section:
    result = aastex.Section("Conclusions")
    result.append(r"""
\begin{outline}
\item Summarize the measured flows, topology, and temperature of event E.
\item State the answer to the question posed in the introduction: whether the bidirectional flows
    of event E are organized by the separatrices of the coronal field.
\item Implications for future snapshot spectrographs, including the second flight of \ESIS.
\end{outline}""")
    return result
