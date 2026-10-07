# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`esis-jet-paper` is a **reproducible scientific article**, not a conventional
software library. The `esis_jet_paper` Python package programmatically generates
a complete AAS-journal LaTeX article (text, figures, tables, and numeric values)
analyzing event E, a transition region jet observed by the EUV Snapshot Imaging
Spectrograph (ESIS) during its 2019 September 30 flight.
Calling `esis_jet_paper.pdf()` produces the final `esis-jet.pdf`.

This is one package within the larger Kankelborg-Group workspace (see the parent
`../CLAUDE.md`). Its sibling articles `esis-instrument-paper` and `ccd-noise-paper`
(checked out locally as `ccd-snr-paper`) follow the same layout and are the
templates it was made from.

## The analysis

The article has three strands, each of which belongs in a library rather than in
this repository:

- **Doppler shifts** of event E from the ESIS images, inverted into spectral
  cubes with the multiplicative algebraic reconstruction technique (MART). The
  inversion lives in `ctis`, and the flight data and Level-4 product in `esis`.
- **Magnetic topology**: separatrices of the coronal field computed from
  SDO/HMI magnetograms with magnetic charge topology. HMI access lives in
  `solar-dynamics-observatory` (`sdo`).
- **Temperature**: differential emission measures from SDO/AIA, Hinode/XRT,
  and ESIS. The inversion lives in `utu`, and the AIA responses in `sdo`.

## Rules

- **Push reusable functionality down the stack**: if a figure or quantity needs a
  capability the libraries lack, add it there (with tests) rather than writing
  bespoke code here. This repo should contain only prose, `aastex` document
  assembly, and thin glue that calls library functions.
- **Every number in the prose is an `aastex.Variable`** defined in `_variables.py`.
  A number the analysis cannot supply yet is declared with `_pending()`, which
  renders as a bold `XX`, so the draft shows plainly what is still owed.
- Sections not yet written are drafted as an `outline` environment (defined in
  `_preamble.py`), which renders as a gray bulleted list, so the plan cannot be
  mistaken for the article.

## Commands

Run from this package directory:

```bash
pip install -e .[test]          # install for development
pytest                          # run tests; test_pdf compiles the LaTeX → PDF
black esis_jet_paper            # format (CI enforces --check)
ruff check                      # lint (CI enforces)
```

Building the PDF requires a **LaTeX installation** with `latexmk` (TeX Live:
`texlive-publishers texlive-science cm-super latexmk`). Without `latexmk`,
`pylatex` falls back to a single `pdflatex` pass and the bibliography is
silently missing; `test_pdf` checks for this.

## Architecture

The whole article is assembled in `_document.py`: `document()` builds an
`aastex.Document`, appending acronyms, variables, title, authors, abstract,
keywords, each section, the acknowledgments, and finally the bibliography
(`sources.bib`). `pdf()` renders it.

- **`sections/`** — each module returns an `aastex.Section` (or `aastex.Abstract`).
  Prose lives here as raw LaTeX strings (with `\cite`, `\ref`, equations) and
  embeds figures/tables by calling the corresponding factory.
- **`figures/`** — each module builds a matplotlib figure and wraps it in an
  `aastex.Figure`/`FigureStar` with a caption.
- **`tables/`** — factories returning `aastex.Table` objects.
- **`_variables.py`** — `aastex.Variable` LaTeX macros for every numeric value
  cited in the prose.
- **`_acronyms.py`** — `aastex.Acronym` definitions; prose uses `\ACRONYM` macros.
- **`_preamble.py`** — custom commands, including a colored comment macro per
  author (`\roy`, `\charles`, `\jake`, `\dana`).

## Movies

No PDF reader plays a movie, and neither does arXiv's HTML version of an article,
so before publication the movies of animated figures can only be watched where we
publish them. Give the figure an `aastex.Animation` (needs `aastex>=0.8`) whose
`url` is `esis_jet_paper.url("<movie>.mp4")`:

```python
figure = aastex.FigureStar(
    "eventE",
    animation=aastex.Animation(movie, url=esis_jet_paper.url(movie.name)),
)
```

`aastex` wraps the stills in AASTeX's `interactive` environment, links the movie
from the caption, and copies it beside the PDF. CI publishes every `.mp4` beside
`esis-jet.pdf` on GitHub Pages, at the root for `main` and under `pr/<number>/`
for a pull request; `ESIS_JET_PAPER_URL`, set by the `tests` workflow, makes the
captions of a pull request link to its own preview. The AAS journals want the
caption to describe what the animation shows and how long it runs, not only that
it exists, and `generate_archive()` packs each movie as `figNNanim.zip` for
submission.

## Conventions

- Every module declares an explicit `__all__` and exposes functionality through small
  factory functions, re-exported up the package via `__init__.py`. To add a new
  figure/table/section: create `_name.py`, then add it to the subpackage `__init__.py`.
- Modules import the top-level package as `import esis_jet_paper` and reach back
  into it (`esis_jet_paper.figures.x()`) rather than deep relative imports.
- Cite only entries in `sources.bib`, and add new ones from the publisher's
  record (e.g. `curl -LH "Accept: application/x-bibtex" https://doi.org/<doi>`)
  rather than typing them by hand.
- Generated LaTeX/PDF output and caches are gitignored — never commit build artifacts.
- Stage explicit files with `git add`; never `git add` whole directories.
