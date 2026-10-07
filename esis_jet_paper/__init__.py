"""
Create the figures and compile the LaTeX files for this article.
"""

from . import figures, sections, tables
from ._acknowledgments import acknowledgments
from ._acronyms import acronyms
from ._authors import authors
from ._document import document, pdf
from ._keywords import keywords
from ._preamble import preamble
from ._url import url
from ._variables import variables

__all__ = [
    "acknowledgments",
    "acronyms",
    "authors",
    "document",
    "figures",
    "keywords",
    "pdf",
    "preamble",
    "sections",
    "tables",
    "url",
    "variables",
]
