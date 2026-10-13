import aastex
import astropy.units as u
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np

import esis_jet_paper

__all__ = [
    "temperature_max",
    "temperature_min",
    "temperature_responses",
]

_label_esis = r"ESIS lines, to come"
"""The label of the lines of ESIS, whose line list is not ready yet."""


def _logt() -> na.AbstractScalar:
    """The log T of each temperature of :func:`esis_jet_paper.temperature_response`."""
    return np.log10(esis_jet_paper.temperature_response().inputs / u.K)


def temperature_min() -> float:
    """The lowest log T of the responses, that of the inversion."""
    return round(float(_logt().min().ndarray), 2)


def temperature_max() -> float:
    """The highest log T of the responses, that of the inversion."""
    return round(float(_logt().max().ndarray), 2)


def temperature_responses() -> aastex.Figure:
    """
    The temperature response of each EUV channel of AIA and of XRT from which
    the DEM of event E is inverted, with a line kept for the lines of ESIS.
    """
    response = esis_jet_paper.temperature_response()
    logt = _logt()
    wavelength = esis_jet_paper.channels.ndarray
    channels = [
        (rf"{w.to_value(u.AA):.0f}\,\AA", esis_jet_paper.color_aia(w))
        for w in wavelength
    ]
    channels.append(("XRT", esis_jet_paper.color_xrt))

    fig, ax = plt.subplots(
        figsize=(aastex.column_width_inches, 0.85 * aastex.column_width_inches),
        constrained_layout=True,
    )
    for c, (label, color) in enumerate(channels):
        na.plt.plot(
            logt,
            response.outputs[{"channel": c}],
            axis="temperature",
            ax=ax,
            color=color,
            label=label,
        )
    # Kept for the lines of ESIS, whose line list is not ready yet.
    ax.plot([], [], color=esis_jet_paper.color_esis, label=_label_esis)

    peak = float(response.outputs.max().ndarray.value)
    ax.set_yscale("log")
    ax.set_ylim(peak / 1e5, 2 * peak)
    ax.set_xlim(temperature_min(), temperature_max())
    ax.set_xlabel(r"$\log_{10} T$")
    ax.set_ylabel(
        r"response ($\mathrm{DN\,cm^{5}\,s^{-1}\,sr^{-1}}$)",
    )
    fig.legend(
        *ax.get_legend_handles_labels(),
        loc="outside upper center",
        ncols=3,
    )

    result = aastex.Figure("fig:temperatureResponses", position="t")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
The temperature responses from which the \DEM\ of event E is inverted, per unit emission measure
and per steradian, from $\log_{10} T = \temperatureResponsesMin$ to \temperatureResponsesMax:
each \EUV\ channel of \AIA, labeled by its wavelength, as computed by SolarSoft
\citep{Boerner2012}, normalized to \EVE\ \citep{Woods2012} and corrected for the emission missing
from CHIANTI, and \XRT\ Al\_poly, as computed by xrtpy \citep{Narukage2011}, with the
contamination on the date of the flight.
\AIA\ \SI{304}{\angstrom} is left out, since \HeII\ is optically thick.
\roy{The \ESIS\ lines of \OIII, \OIV, \OV, and \MgX\ are left out until the \ESIS\ line list is
ready.
The \AIA\ and \XRT\ responses come from different versions of CHIANTI, where the outline calls
for one.}
"""))
    return result
