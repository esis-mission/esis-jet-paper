import pytest

import esis_jet_paper


def test_url_default(monkeypatch: pytest.MonkeyPatch):
    """A local build links to the article built from main."""
    monkeypatch.delenv("ESIS_JET_PAPER_URL", raising=False)
    result = esis_jet_paper.url("event-e.mp4")
    assert result == "https://esis-mission.github.io/esis-jet-paper/event-e.mp4"


@pytest.mark.parametrize(
    argnames="base",
    argvalues=[
        "https://esis-mission.github.io/esis-jet-paper/pr/7/",
        "https://esis-mission.github.io/esis-jet-paper/pr/7",
    ],
)
def test_url_pull_request(monkeypatch: pytest.MonkeyPatch, base: str):
    """A pull request links to its own preview, with or without a slash."""
    monkeypatch.setenv("ESIS_JET_PAPER_URL", base)
    result = esis_jet_paper.url("event-e.mp4")
    assert result == "https://esis-mission.github.io/esis-jet-paper/pr/7/event-e.mp4"
