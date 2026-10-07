# esis-jet-paper

[![tests](https://github.com/esis-mission/esis-jet-paper/actions/workflows/tests.yml/badge.svg)](https://github.com/esis-mission/esis-jet-paper/actions/workflows/tests.yml)
[![Black](https://github.com/esis-mission/esis-jet-paper/actions/workflows/black.yml/badge.svg)](https://github.com/esis-mission/esis-jet-paper/actions/workflows/black.yml)
[![Ruff](https://github.com/esis-mission/esis-jet-paper/actions/workflows/ruff.yml/badge.svg)](https://github.com/esis-mission/esis-jet-paper/actions/workflows/ruff.yml)

An AAS journal article analyzing event E, a transition region jet observed by
the EUV Snapshot Imaging Spectrograph (ESIS) during its 2019 September 30
sounding rocket flight.

Roy T. Smart, Charles C. Kankelborg, Jacob D. Parker, and Dana W. Longcope

📄 **[Read the article (pdf)](https://esis-mission.github.io/esis-jet-paper/esis-jet.pdf)**

## What this is

ESIS is a slitless spectrograph which records several dispersed images of
the transition region at once, so that a spectral cube of the whole field
can be recovered from a single exposure. This article uses that capability
to study one event, event E, in three ways:

- **Flows.** The ESIS images are inverted into spectral cubes with the
  multiplicative algebraic reconstruction technique (MART), and the Doppler
  shifts of the event are measured from them.
- **Magnetic topology.** The separatrices of the coronal field are computed
  from SDO/HMI magnetograms using magnetic charge topology, and compared
  with where the flows are.
- **Temperature.** Differential emission measures are computed from SDO/AIA,
  Hinode/XRT, and ESIS together, to find how hot the event gets.

## This repository *is* the article

Every figure, table, and numeric value in the prose is computed at build time
by the `esis_jet_paper` package, so the text cannot drift away from the
analysis. Numbers reach the prose as `aastex.Variable` macros rather than as
literals; a quantity the analysis has not produced yet is rendered as a bold
**XX**. Sections not yet written appear in the PDF as a gray outline.

```python
import esis_jet_paper
esis_jet_paper.pdf()
```

| path | contents |
|---|---|
| `_document.py` | assembles the article and renders the pdf |
| `sections/` | the prose, as LaTeX strings, one module per section |
| `figures/` | one module per figure, each returning an `aastex.Figure` |
| `tables/` | one module per table |
| `_variables.py` | the `aastex.Variable` macros quoted in the prose |
| `_acronyms.py` | acronym definitions used as `\ACRONYM` macros |
| `_preamble.py` | custom commands, including a comment macro per author |
| `sources.bib` | the bibliography |

The analysis itself belongs in the group's libraries, not here:
[`esis`](https://github.com/esis-mission/esis) for the flight data,
[`ctis`](https://github.com/sun-data/ctis) for the MART inversion,
[`solar-dynamics-observatory`](https://github.com/sun-data/solar-dynamics-observatory)
for AIA and HMI, and [`utu`](https://github.com/sun-data/utu) for the DEMs.

## Building

Requires Python 3.12 or newer and a LaTeX installation. On Ubuntu:

```bash
sudo apt-get install latexmk texlive-publishers texlive-science cm-super
```

`latexmk` is not optional. Without it `pylatex` falls back to a single
`pdflatex` pass, which silently produces an article with no bibliography.

```bash
pip install -e .[test]
pytest                       # builds and validates the pdf
black esis_jet_paper         # formatting, enforced in CI
ruff check                   # linting, enforced in CI
```

## Continuous integration

Every push runs the test suite, which builds the article and checks that no
citation or cross-reference is left unresolved. Pushes to `main` publish the
article to the link above, and pull requests get their own preview at
`…/pr/<number>/esis-jet.pdf`, linked in a comment on the pull request and
removed when it closes.

## Commenting on the draft

Each author has a colored comment macro for notes in the prose:
`\roy{...}`, `\charles{...}`, `\jake{...}`, and `\dana{...}`.
