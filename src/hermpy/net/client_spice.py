import re
from contextlib import contextmanager
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict
from urllib.request import urlopen

import spiceypy as spice

from hermpy.utils import download_files

#: Default remote kernel sources used by :class:`ClientSPICE` when no
#: ``KERNEL_LOCATIONS`` argument is provided. Includes the standard NAIF
#: generic kernels for leap seconds (LSK), planetary constants (PCK), and
#: planetary ephemerides (SPK). Each entry requires ``BASE``, ``DIRECTORY``,
#: and ``PATTERNS`` keys — see :class:`ClientSPICE` for details.
DEFAULT_KERNEL_LOCATIONS: Dict[str, Dict[str, Any]] = {
    "Generic (tls)": {
        "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
        "DIRECTORY": "generic_kernels/lsk/",
        "PATTERNS": ["naif????.tls", "latest_leapseconds.tls"],
    },
    "Generic (tpc)": {
        "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
        "DIRECTORY": "generic_kernels/pck/",
        "PATTERNS": ["pck00011.tpc"],
    },
    "Generic (bsp)": {  # Planets
        "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
        "DIRECTORY": "generic_kernels/spk/planets/",
        "PATTERNS": ["de442.bsp"],
    },
}


class ClientSPICE:
    """
    Client for managing and loading SPICE kernels from remote and local sources.

    Handles downloading kernels from NAIF (or other configured sources),
    resolving filename patterns against remote directory listings, and
    furnishing the resulting files to SpiceyPy via a context manager.
    """

    def __init__(
        self, KERNEL_LOCATIONS: Dict[str, Dict[str, Any]] = DEFAULT_KERNEL_LOCATIONS
    ):
        #: Remote kernel source configurations keyed by human-readable label.
        #: Each entry requires three keys: ``BASE`` (root URL), ``DIRECTORY``
        #: (path under base), and ``PATTERNS`` (filename patterns to resolve
        #: against the remote directory listing).
        self.KERNEL_LOCATIONS = KERNEL_LOCATIONS

        self._query_buffer: list[str] = []
        self._local_buffer: list[Path] = []

    def add_local_kernels(self, paths: list[Path]) -> None:
        """
        Stages local kernel files to be furnished on the next fetch.

        Files are held in an internal buffer and included alongside any
        remotely downloaded kernels when fetch() is called.
        """

        self._local_buffer.extend(paths)

    def fetch(self) -> list[str]:
        """
        Resolves, downloads, and returns all kernel file paths.

        Expands each configured source's filename patterns against its remote
        directory listing, downloads any files not already cached, appends any
        staged local kernels, and clears the remote query buffer. Returns the
        combined list of absolute file paths ready to be furnished to SpiceyPy.
        """

        all_urls: list[str] = []

        for cfg in self.KERNEL_LOCATIONS.values():
            base = cfg["BASE"]
            directory = cfg["DIRECTORY"]
            patterns = cfg["PATTERNS"]

            all_urls.extend(expand_patterns(base, directory, patterns))

        self._query_buffer.extend(all_urls)

        files = download_files(self._query_buffer)

        # Return downloaded paths and anything in the local buffer.
        return files + [str(p) for p in self._local_buffer]

    # We want this class to be able to function as a spiceypy.KernelPool()
    @contextmanager
    def KernelPool(self):
        """
        Context manager that furnishes all configured kernels for the duration
        of the block.

        Calls fetch() to resolve and download kernels, then delegates to
        spiceypy.KernelPool so that all furnished kernels are automatically
        unloaded on exit. Use this as the standard entry point for any SPICE
        computation that requires this client's kernel set.

        Example:
            with client.KernelPool():
                et = spice.utc2et("2024-01-01")
        """

        with spice.KernelPool(self.fetch()):
            yield


def list_remote_files(url: str) -> list[str]:
    """Return filenames from a simple Apache-style directory listing."""

    with urlopen(url) as f:
        html = f.read().decode("utf-8")

    # Extract href targets
    return re.findall(r'href="([^"/]+)"', html)


def expand_patterns(base_url: str, directory: str, patterns: list[str]) -> list[str]:
    full_dir_url = base_url + directory
    files = list_remote_files(full_dir_url)

    matched = []
    for pattern in patterns:
        # Check first if file exists
        hits = [f"{full_dir_url}{fname}" for fname in files if fnmatch(fname, pattern)]

        if not hits:
            raise FileNotFoundError(
                f"No remote files matched pattern '{pattern}' in {full_dir_url}"
            )

        matched.extend(hits)

    return matched
