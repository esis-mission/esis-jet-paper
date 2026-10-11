import csv
import functools
import hashlib
import pathlib
import shutil
import tarfile
import urllib.request

import astropy.units as u
import hinode
import named_arrays as na
import numpy as np
import sdo

__all__ = [
    "aia",
    "archive",
    "channels",
    "directory_default",
    "xrt",
]

directory_default = pathlib.Path.home() / ".esis_jet_paper"
"""Where the data this article downloads is kept."""

channels = na.ScalarArray([94, 131, 171, 193, 211, 335] * u.AA, axes="channel")
"""The EUV channels of AIA which the differential emission measure uses."""

_tag = "event-e-v1.0"
"""The release of ``esis-data-2019`` which holds the images of event E."""

_url_archive = (
    "https://github.com/esis-mission/esis-data-2019/releases/download/"
    f"{_tag}/esis-2019-event-e.tar"
)
"""Where the archive of the images of event E is published."""

_sha256_archive = "11ea0e91104e3daf0849c8e397ee27b97482bf28c8802e4147c34dacb6caa941"
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
    The directory holding the AIA and XRT images of event E from 18:00 to
    18:20 UT, the ``event-e-v1.0`` release of ``esis-data-2019``,
    downloaded and unpacked the first time it is needed.

    The archive holds every Al_poly image of XRT which began in that time,
    unchanged, in ``xrt/``, and cutouts around event E of the registered
    images of seven EUV channels of AIA in ``aia/``,
    each with a manifest of where its files came from.

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


@functools.cache
def aia() -> sdo.aia.Filtergram:
    """
    The registered images of the :data:`channels` of AIA in every 12 second
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
    paths = [[files[s, int(c)] for c in channels.ndarray.value] for s in slots]
    return sdo.aia.Filtergram.from_fits(
        path=na.ScalarArray(np.array(paths, dtype=object), axes=("time", "channel")),
        wavelength=channels,
        axis_time="time",
        axis_wavelength="channel",
    )
