import aastex

import esis_jet_paper


def test_temperature_responses():
    """The figure spans the temperatures of the inversion."""
    figure = esis_jet_paper.figures.temperature_responses()
    assert isinstance(figure, aastex.Figure)
    assert figure.animation is None
    module = esis_jet_paper.figures._temperature_responses
    assert module.temperature_min() == 5.0
    assert module.temperature_max() == 7.5
