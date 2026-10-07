import aastex

__all__ = [
    "inversion",
]


def inversion() -> aastex.Section:
    result = aastex.Section("Spectral Inversion and Doppler Shifts")
    result.append(r"""
\begin{outline}
\item \textbf{Forward model.}
    Each \ESIS\ channel records a dispersed image of the field, so the images are a linear function of
    the spectral radiance $I(x, y, \lambda)$.
    Describe the model of that function built from the flight optics (the \texttt{esis} and
    \texttt{optika} packages), including the point-spread function and the vignetting.
\item \textbf{The \MART\ inversion} \citep{Gordon1970,Okamoto1991}, implemented in the
    \texttt{ctis} package.
    The update rule, the initial guess, and the stopping criterion.
    The reconstructed cubes sample the sky every \ang{;;0.75} and the line of sight every
    \SI{17.5}{\kilo\meter\per\second} over $\pm$\SI{210}{\kilo\meter\per\second} about each line,
    in five spectral windows, and are reconstructed independently at each exposure.
    How the blend of \OIV\ and \MgX\ near \SI{610}{\angstrom} is handled, and why the radiometry of the
    channels is relative, so that velocities are trusted further than intensities.
\item \textbf{Validation.}
    Invert synthetic \ESIS\ images of a known scene containing a bidirectional jet, and report how
    well the recovered Doppler shifts and widths match the truth as a function of brightness and
    velocity.
    This sets the uncertainties quoted for event E, and the speed beyond which a fast component is
    poorly constrained by the spectral window.
\item \textbf{Doppler shifts of event E.}
    Line-of-sight velocity and width maps from the inverted cubes, from moments and from fits of
    two Gaussian components to each \OV\ profile, a core near rest and a fast component.
    Peak speeds of the blue and red components (\velocityBlue\ and \velocityRed).
    Preliminary fits find blue wings reaching about \SI{150}{\kilo\meter\per\second} and a separate
    red component near \SI{100}{\kilo\meter\per\second}, while the median Doppler shift, which moves
    only part of the way toward a fast component in one wing, peaks near
    \SI{60}{\kilo\meter\per\second}; settle which of these the article quotes.
\item \textbf{Other lines.}
    The red-shifted footpoint appears in \OIII\ and \OIV, while the blue-shifted material at the cusp
    is seen only in \OV\ and faintly in \HeI; whether this is a matter of brightness or of
    temperature.
\item \textbf{Motion.}
    The plane-of-sky speed of the blue-shifted component, combined with its line-of-sight speed into
    a three-dimensional velocity.
\item \textbf{Figures:} the inverted line profiles at a few points in the event;
    a time series of Doppler maps of event E; the plane-of-sky track of the fast components.
\end{outline}""")
    return result
