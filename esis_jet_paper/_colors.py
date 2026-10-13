import astropy.units as u
import matplotlib.colors
import sunpy.visualization.colormaps.color_tables

__all__ = [
    "color_aia",
    "color_esis",
    "color_xrt",
]

_levels = {
    94: 0.4,
    131: 0.55,
    171: 0.69,
    193: 0.4,
    211: 0.25,
    304: 0.69,
    335: 0.3,
}
"""
The level of the AIA color table of each channel, keyed by its wavelength in
angstroms, at which its line takes its color.
Each is where the table is most colorful, except that 131 Å is lighter and
335 Å darker, so that the two are not alike.
"""


def color_aia(wavelength: u.Quantity) -> str:
    """
    The color of the line of the AIA channel at `wavelength`, taken from its
    color table, the same in every figure.

    Parameters
    ----------
    wavelength
        The wavelength of the channel, one of the EUV channels of AIA.
    """
    table = sunpy.visualization.colormaps.color_tables.aia_color_table(wavelength)
    level = _levels[round(wavelength.to_value(u.AA))]
    return matplotlib.colors.to_hex(table(level))


color_xrt = "black"
"""The color of the line of XRT, the same in every figure."""

color_esis = "#c000c0"
"""
The color of the line of ESIS, the same in every figure, unlike any of the
AIA color tables and unlike the gray which the figures give the median.
"""
