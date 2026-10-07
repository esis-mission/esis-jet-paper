"""
The sections of this article, each a factory function returning an
:class:`aastex.Section`.
"""

from ._s0_abstract import abstract
from ._s1_introduction import introduction
from ._s2_observations import observations
from ._s3_inversion import inversion
from ._s4_topology import topology
from ._s5_temperature import temperature
from ._s6_discussion import discussion
from ._s7_conclusions import conclusions

__all__ = [
    "abstract",
    "conclusions",
    "discussion",
    "introduction",
    "inversion",
    "observations",
    "temperature",
    "topology",
]
