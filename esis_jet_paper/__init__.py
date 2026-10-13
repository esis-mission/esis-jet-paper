"""
Create the figures and compile the LaTeX files for this article.
"""

from . import figures, sections, tables
from ._acknowledgments import acknowledgments
from ._acronyms import acronyms
from ._authors import authors
from ._data import aia, archive, channels, directory_default, xrt
from ._dem import Inversion, dem
from ._document import document, pdf
from ._keywords import keywords
from ._preamble import preamble
from ._style import rc
from ._url import url
from ._variables import variables

__all__ = [
    "Inversion",
    "acknowledgments",
    "acronyms",
    "aia",
    "archive",
    "authors",
    "channels",
    "dem",
    "directory_default",
    "document",
    "figures",
    "keywords",
    "pdf",
    "preamble",
    "rc",
    "sections",
    "tables",
    "url",
    "variables",
    "xrt",
]
