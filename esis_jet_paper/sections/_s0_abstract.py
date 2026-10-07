import aastex

__all__ = [
    "abstract",
]


def abstract() -> aastex.Abstract:
    result = aastex.Abstract()
    result.append(r"""
Jets and explosive events in the solar transition region are thought to be driven by magnetic
reconnection, but the spatial structure of their flows is difficult to observe, since a slit
spectrograph records it one position at a time.
The EUV Snapshot Imaging Spectrograph (ESIS) is a slitless, computed tomography imaging spectrograph
which recorded the quiet Sun near disk center in \OV\ \SI{630}{\angstrom} and several other
transition region and coronal lines across a wide field of view during a sounding rocket flight on
2019 September 30.
The largest event it observed, event E, is a jet with an inverted-Y morphology which lasted
\eventDuration\ and extended \eventLength.
We invert the ESIS images into spectral cubes using the multiplicative algebraic reconstruction
technique (MART), and measure Doppler shifts of up to \velocityBlue\ toward and \velocityRed\ away
from the observer.
We compute the magnetic topology beneath the event from SDO/HMI magnetograms using magnetic charge
topology, and compare the separatrices of the coronal field with the locations of the flows.
We combine intensities from SDO/AIA, Hinode/XRT, and ESIS to compute differential emission measures
of the event, and find a peak temperature of \temperaturePeak.
\roy{One or two sentences of conclusions: whether the flows are organized by the separatrices,
and what the temperature implies about the coronal counterpart of the jet.}
\acresetall""")
    return result
