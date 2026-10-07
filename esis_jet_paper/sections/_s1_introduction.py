import aastex

__all__ = [
    "introduction",
]


def introduction() -> aastex.Section:
    result = aastex.Section("Introduction")
    result.append(r"""
The solar \TR\ is host to a variety of small, transient phenomena whose spectral line profiles
reveal flows of order \SI{100}{\kilo\meter\per\second}.
Explosive events, first observed by the \HRTS\ as high-velocity jets in the quiet Sun
\citep{Brueckner1983}, are compact, short-lived brightenings whose line profiles are broadened
into one or both wings by Doppler shifts of about this size \citep{Dere1989}.
\citet{Innes1997} found that the blue- and red-shifted emission of these events is separated along
the slit, as expected of the bidirectional outflows from a reconnection site, and explosive events
have since been widely interpreted as the signature of magnetic reconnection in the \TR\
\citep{Dere1991,Innes2015}.
They are associated with the evolution of the photospheric magnetic field \citep{Muglach2008},
and a compact \TR\ brightening has been found to occur in a magnetic field with a fan-spine topology
\citep{Chitta2017}.

Jets are related, collimated phenomena which are observed across a wide range of temperatures,
from network jets in the \TR\ \citep{Tian2014} to coronal X-ray jets
\citep{Shibata1992,Raouafi2016}.
Coronal jets commonly have an inverted-Y morphology, which is interpreted as reconnection between a
small closed bipole and the surrounding large-scale field \citep{Shibata1992,Raouafi2016}, at a
null point whose
fan surface divides the two flux systems \citep{Pariat2009}.
They are divided into standard and blowout jets \citep{Moore2010}, and many have been found to be
driven by the eruption of a minifilament, in coronal holes \citep{Sterling2015}, in active regions
\citep{Sterling2016}, and in the quiet Sun, where the eruption is triggered by flux cancellation
\citep{Panesar2016}.
The breakout model unifies these observations as reconnection at a null point above an erupting
filament channel \citep{Wyper2017,Wyper2018}.
Whether explosive events, network jets, and coronal jets are the same process at different scales
remains open \citep{Chen2019}, and one part of that question is whether explosive events have a
coronal counterpart at all \citep{Teriaca2002}.

These models make specific predictions about where flows should appear relative to the magnetic
structure, and testing them requires the spectrum at every point of an event at the same time.
A slit spectrograph samples only one position at a time, so a raster across an evolving event
conflates its spatial and temporal structure, while an imager records the morphology of the event
but measures flows only in the plane of the sky.
\ESISCapital\ was designed to resolve this ambiguity.
It is a slitless spectrograph which records several dispersed images of the Sun at once, each
dispersed in a different direction, from which a spectral cube of the whole field can be recovered
in the manner of a \CTIS\ \citep{Okamoto1991,Descour1995}.
It is the successor to \MOSES\ \citep{Kankelborg2001}, whose flights recorded explosive events in
\HeII\ \SI{304}{\angstrom} \citep{Fox2010,Rust2019} and showed how the spectral content of
overlapping images can be recovered \citep{Courrier2018,ParkerKankelborg2022}.

\ESISCapital\ flew for the first time on 2019 September 30.
\citet{Parker2022} reported the first results of that flight, including the Doppler shifts of
several explosive events in \OV\ \SI{630}{\angstrom}, and identified among them event E, the largest
and most complex velocity event the instrument observed.
In the images of event E they found a strong redshift at its brightest point and faint, blue-shifted
material rising from it along a thin structure which is also visible in \AIA\ images, which they
suggested might be a small jet or minifilament eruption \citep{Sterling2015}.
Its complexity defeated an interpretation from the images alone, and they deferred its analysis to
a future publication.
Here we recover its spectra by inverting the \ESIS\ images with the \MART\
\citep{Gordon1970,Okamoto1991}, which reconstructs the spectral cube at every exposure.

If event E is driven by reconnection, its flows should originate where reconnection can occur.
In \MCT\ \citep{Longcope2002,Longcope2005}, the photospheric field is represented by discrete
magnetic sources, and the potential coronal field above them is divided into domains of distinct
connectivity by separatrix surfaces, which intersect along separators where reconnection transfers
flux between domains.
\MCTCapital\ has been applied to active regions \citep{Barnes2005}, and the X-ray brightness of
coronal bright points is consistent with the energy released by reconnection at the separator
between a converging pair of sources \citep{Longcope2001}.
Computed from \HMI\ magnetograms \citep{Scherrer2012} beneath event E, the separatrices predict where
its bidirectional flows should be, and the Doppler maps from \ESIS\ show where they are.

A second question is how hot the event becomes.
\DEMCapitals\ are routinely computed from the \EUV\ channels of \AIA\ \citep{Lemen2012} using a variety of
methods \citep{Hannah2012,Plowman2013,Cheung2015,Plowman2020}, but those channels are dominated by
coronal lines and constrain the \TR\ poorly, while \XRT\ \citep{Golub2007} is sensitive to the
hottest plasma.
The \ESIS\ passband contains lines of \HeI, \OIII, \OIV, \OV, and \MgX, which together span the
\TR\ and the low corona, so that combining all three instruments constrains the \DEM\ of the event
from the \TR\ to the corona.

In this paper we analyze event E with all three of these tools.
Section~\ref{sec:Observations} describes the observations from \ESIS, \AIA, \HMI, and \XRT\ and gives
an overview of the event.
Section~\ref{sec:SpectralInversionandDopplerShifts} describes the inversion of the \ESIS\ images
and the Doppler shifts of the event,
Section~\ref{sec:MagneticTopology} the magnetic topology computed from \HMI,
and Section~\ref{sec:Temperature} the \DEMs.
We discuss what they imply about the mechanism of the event in Section~\ref{sec:Discussion} and
conclude in Section~\ref{sec:Conclusions}.""")
    return result
