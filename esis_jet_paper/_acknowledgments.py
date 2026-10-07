import aastex

__all__ = [
    "acknowledgments",
]


def acknowledgments() -> aastex.Acknowledgments:
    """
    The acknowledgments of this article.
    """
    result = aastex.Acknowledgments()
    result.append(r"""
\roy{Grant numbers for the ESIS flight and analysis.}
\textit{SDO} is a mission of NASA's Living With a Star program, and the \AIA\ and \HMI\ data are
courtesy of NASA/SDO and the \AIA\ and \HMI\ science teams.
\textit{Hinode} is a Japanese mission developed and launched by ISAS/JAXA, with NAOJ as domestic
partner and NASA and STFC (UK) as international partners.
It is operated by these agencies in co-operation with ESA and NSC (Norway).
This article is an executable paper: every figure, table, and number in it is computed from the
data when the article is built, and the code that builds it is available at
\url{https://github.com/esis-mission/esis-jet-paper}.""")
    return result
