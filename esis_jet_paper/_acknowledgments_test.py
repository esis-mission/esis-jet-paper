import aastex

import esis_jet_paper


def test_acknowledgments() -> None:
    """
    The acknowledgments are the AASTeX environment, with the grants and the
    address of the code that builds the article.
    """
    result = esis_jet_paper.acknowledgments()
    assert isinstance(result, aastex.Acknowledgments)
    result = result.dumps()
    for grant in ["NNX14AK71G", "80NSSC17K0524"]:
        assert grant in result
    assert r"\url{https://github.com/esis-mission/esis-jet-paper}" in result
