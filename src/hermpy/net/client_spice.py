import os
import re
from contextlib import contextmanager
from fnmatch import fnmatch
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import spiceypy as spice
from astropy.utils.data import conf as astropy_data_conf
from astropy.utils.data import download_files_in_parallel

from hermpy.utils.os import get_multiprocessing_start_method

# Increase astropy remote timeout
astropy_data_conf.remote_timeout = 120


class ClientSPICE:
    def __init__(
        self,
        KERNEL_LOCATIONS: dict[str, dict[str, Any]] = {
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
        },
    ):
        self.KERNEL_LOCATIONS = KERNEL_LOCATIONS
        self._query_buffer: list[str] = []
        self._local_buffer: list[Path] = []

    def add_local_kernels(self, paths: list[Path]) -> None:
        """
        Adds files to _local_buffer to be loaded when fetched.
        """

        self._local_buffer.extend(paths)

    def flush_local_kernel_buffer(self) -> None:
        """
        Flush the local kernel buffer.
        """
        self._local_buffer: list[Path] = []

    def fetch(self, check_for_updates: bool = False) -> list[str]:
        """
        Download and fetch files in self.query_buffer and clears the buffer. If
        files are already downloaded, fetch them.
        """
        all_urls: list[str] = []
        for cfg in self.KERNEL_LOCATIONS.values():
            base = cfg["BASE"]
            directory = cfg["DIRECTORY"]
            patterns = cfg["PATTERNS"]
            all_urls.extend(expand_patterns(base, directory, patterns))
        self._query_buffer.extend(all_urls)

        cache = "update" if check_for_updates else True
        force_serial = os.environ.get("CI") or os.environ.get("READTHEDOCS")

        if force_serial or len(self._query_buffer) <= 1:
            from astropy.utils.data import download_file

            data_paths = [
                str(download_file(url, cache=cache, pkgname="hermpy"))
                for url in self._query_buffer
            ]
        else:
            data_paths = list(
                download_files_in_parallel(
                    self._query_buffer,
                    cache=cache,
                    pkgname="hermpy",
                    multiprocessing_start_method=get_multiprocessing_start_method(),
                )
            )

        return data_paths + [str(p) for p in self._local_buffer]

    # We want this class to be able to function as a spiceypy.KernelPool()
    @contextmanager
    def KernelPool(self):
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
