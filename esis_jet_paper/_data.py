import csv
import functools
import hashlib
import pathlib
import shutil
import tarfile
import urllib.request

import astropy.io.fits
import astropy.units as u
import hinode
import named_arrays as na
import numpy as np
import sdo

__all__ = [
    "aia",
    "aia_304",
    "archive",
    "channels",
    "directory_default",
    "hmi",
    "xrt",
]

directory_default = pathlib.Path.home() / ".esis_jet_paper"
"""Where the data this article downloads is kept."""

channels = na.ScalarArray([94, 131, 171, 193, 211, 335] * u.AA, axes="channel")
"""The EUV channels of AIA which the differential emission measure uses."""

_tag = "event-e-v1.1"
"""The release of ``esis-data-2019`` which holds the images of event E."""

_url_archive = (
    "https://github.com/esis-mission/esis-data-2019/releases/download/"
    f"{_tag}/esis-2019-event-e.tar"
)
"""Where the archive of the images of event E is published."""

_sha256_archive = "1cb9bb2660da667096c368059f033b73bf639a56ecc9338705d15b9636ad8ed2"
"""The SHA-256 checksum of the archive at :data:`_url_archive`."""


def _sha256(path: pathlib.Path) -> str:
    """The SHA-256 checksum of a file, read a piece at a time."""
    result = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(2**20), b""):
            result.update(chunk)
    return result.hexdigest()


def archive(directory: None | pathlib.Path = None) -> pathlib.Path:
    """
    The directory holding the images of event E, the ``event-e-v1.1``
    release of ``esis-data-2019``, downloaded and unpacked the first time it
    is needed.

    The archive holds every Al_poly image of XRT which began from 18:00 to
    18:20 UT, unchanged, in ``xrt/``, and cutouts around event E of the
    registered images of seven EUV channels of AIA in ``aia/``.
    Beside them are cutouts of the registered line-of-sight magnetograms of
    HMI, every 45 seconds over the same time in ``hmi/`` and every 720
    seconds over the day before in ``hmi_history/``, and the slit-jaw images
    of IRIS at 1400 angstroms, unchanged, in ``iris/``.
    Each directory has a manifest of where its files came from.

    Parameters
    ----------
    directory
        Where to keep the images.
        If :obj:`None` (the default), :data:`directory_default` is used.
    """
    if directory is None:
        directory = directory_default

    result = directory / _tag
    # written last, so that an unpacking which was interrupted is redone
    complete = result / "complete"
    if complete.is_file():
        return result

    directory.mkdir(parents=True, exist_ok=True)
    path = directory / pathlib.Path(_url_archive).name
    partial = path.with_name(path.name + ".part")
    with (
        urllib.request.urlopen(_url_archive, timeout=300) as response,
        open(partial, "wb") as f,
    ):
        shutil.copyfileobj(response, f)
    sha256 = _sha256(partial)
    if sha256 != _sha256_archive:
        partial.unlink()
        raise ValueError(
            f"The archive downloaded from {_url_archive} has the checksum "
            f"{sha256}, not {_sha256_archive}."
        )
    partial.replace(path)

    with tarfile.open(path) as tar:
        tar.extractall(result, filter="data")
    path.unlink()
    complete.touch()

    return result


def _manifest(directory: pathlib.Path) -> list[dict[str, str]]:
    """The rows of the manifest of one directory of :func:`archive`."""
    with open(directory / "manifest.csv", newline="") as f:
        return list(csv.DictReader(f))


@functools.cache
def xrt() -> hinode.xrt.Filtergram:
    """
    The Al_poly images of XRT which began from 18:00 to 18:20 UT, in order
    of time, with the visible light leaking into them subtracted,
    co-aligned with AIA by :func:`hinode.xrt.open`'s default,
    and with what :meth:`hinode.xrt.Filtergram.uncertainty` needs.
    """
    directory = archive() / "xrt"
    rows = sorted(_manifest(directory), key=lambda row: row["DATE_OBS"])
    paths = [str(directory / row["file"]) for row in rows]
    result = hinode.xrt.Filtergram.from_fits(
        path=na.ScalarArray(np.array(paths, dtype=object), axes="time"),
        leak=True,
        uncertainty=True,
    )
    return result.remove_leak()


def _aia(wavelength: na.ScalarArray) -> sdo.aia.Filtergram:
    """
    The registered images of the given channels of AIA in every 12 second
    slot from 17:59:36 to 18:20:36 UT, cut out around event E,
    along the axes ``time`` and ``channel``.
    """
    directory = archive() / "aia"
    files = {}
    for row in _manifest(directory):
        # the record is the series, then the slot, then the channel
        _, slot, channel = row["record"].replace("]", "").split("[")
        files[slot, int(channel)] = str(directory / row["file"])
    slots = sorted({slot for slot, _ in files})
    paths = [[files[s, int(c)] for c in wavelength.ndarray.value] for s in slots]
    return sdo.aia.Filtergram.from_fits(
        path=na.ScalarArray(np.array(paths, dtype=object), axes=("time", "channel")),
        wavelength=wavelength,
        axis_time="time",
        axis_wavelength="channel",
    )


@functools.cache
def aia() -> sdo.aia.Filtergram:
    """
    The registered images of the :data:`channels` of AIA in every 12 second
    slot from 17:59:36 to 18:20:36 UT, cut out around event E,
    along the axes ``time`` and ``channel``.
    """
    return _aia(channels)


@functools.cache
def aia_304() -> sdo.aia.Filtergram:
    """
    The registered images of the 304 angstrom channel of AIA, which the
    differential emission measure leaves out since He II is optically thick,
    like :func:`aia` along the axes ``time`` and ``channel``.
    """
    return _aia(na.ScalarArray([304] * u.AA, axes="channel"))


def _magnetograms(paths: list[pathlib.Path]) -> sdo.hmi.Magnetogram:
    """
    The cutouts of registered magnetograms at `paths`, along the axis
    ``time``.

    :meth:`sdo.hmi.Magnetogram.from_fits` takes the keywords of each file
    from the JSOC, since the files the JSOC serves have none, so here they
    are taken from the header of each cutout instead.
    """
    names = ["DATE-OBS", "BUNIT", "CUNIT1"]
    names += ["CRVAL1", "CRVAL2", "CRPIX1", "CRPIX2", "CDELT1", "CDELT2"]
    keywords = {name: [] for name in names + ["CROTA2"]}
    for path in paths:
        header = astropy.io.fits.getheader(path)
        for name in names:
            keywords[name].append(header[name])
        # Registration rotates each magnetogram to solar north up, and leaves
        # the rotation that remains as a matrix rather than as an angle.
        angle = np.arctan2(header["PC2_1"], header["PC1_1"])
        keywords["CROTA2"].append(np.rad2deg(angle))
    return sdo.hmi.Magnetogram.from_fits(
        path=na.ScalarArray(np.array([str(p) for p in paths], dtype=object), "time"),
        keywords={k: na.ScalarArray(np.array(v), "time") for k, v in keywords.items()},
    )


@functools.cache
def hmi() -> sdo.hmi.Magnetogram:
    """
    The 45 second line-of-sight magnetograms of HMI in every slot from
    18:00:00 to 18:20:15 TAI, in order of time, in gauss, along the axis
    ``time``, on the grid of :func:`aia`.
    """
    directory = archive() / "hmi"
    rows = sorted(_manifest(directory), key=lambda row: row["T_REC"])
    return _magnetograms([directory / row["file"] for row in rows])
