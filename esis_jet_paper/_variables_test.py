import aastex

import esis_jet_paper


def test_variables():
    result = esis_jet_paper.variables()
    assert result
    assert all(isinstance(v, aastex.Variable) for v in result)


def test_variables_unique():
    """A name defined twice would silently take whichever value came last."""
    names = [v.name for v in esis_jet_paper.variables()]
    assert len(names) == len(set(names))
