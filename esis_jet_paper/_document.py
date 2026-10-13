import pathlib

import aastex
import matplotlib.pyplot as plt

import esis_jet_paper

__all__ = [
    "document",
    "pdf",
]


def document(linenumbers: bool = True) -> aastex.Document:
    """
    An :mod:`aastex` representation of the article.

    Parameters
    ----------
    linenumbers
        Whether to number the lines, as the journal requires for review.
    """

    plt.rcParams.update(esis_jet_paper.rc)

    doc = aastex.Document(
        document_options=[
            "twocolumn",
        ],
        lmodern=False,
        textcomp=False,
        linenumbers=linenumbers,
    )

    doc.packages.append(aastex.Package("amsmath"))
    doc.packages.append(aastex.Package("hyperref"))
    doc.packages.append(aastex.Package("siunitx"))

    doc.preamble += esis_jet_paper.preamble()
    doc.preamble += esis_jet_paper.acronyms()

    doc.variables += esis_jet_paper.variables()

    doc.append(
        aastex.Title(
            "Flows, Magnetic Topology, and Temperature of a Transition Region Jet "
            "Observed by the EUV Snapshot Imaging Spectrograph"
        )
    )

    doc += esis_jet_paper.authors()

    doc.append(esis_jet_paper.sections.abstract())
    doc.append(esis_jet_paper.keywords())
    doc.append(esis_jet_paper.sections.introduction())
    doc.append(esis_jet_paper.sections.observations())
    doc.append(esis_jet_paper.sections.inversion())
    doc.append(esis_jet_paper.sections.topology())
    doc.append(esis_jet_paper.sections.temperature())
    doc.append(esis_jet_paper.sections.discussion())
    doc.append(esis_jet_paper.sections.conclusions())
    doc.append(esis_jet_paper.acknowledgments())

    doc.append(aastex.Bibliography("sources"))

    return doc


def pdf(linenumbers: bool = True) -> pathlib.Path:
    """
    Build a pdf version of :func:`document` and return the path of the document.

    Parameters
    ----------
    linenumbers
        Whether to number the lines, as the journal requires for review.
    """

    doc = document(linenumbers=linenumbers)

    path = pathlib.Path(__file__).parent / "esis-jet"
    doc.generate_pdf(
        filepath=path,
        clean_tex=False,
    )

    return path.with_suffix(".pdf")
