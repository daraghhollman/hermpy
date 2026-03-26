import re
from contextlib import contextmanager
from fnmatch import fnmatch
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import spiceypy as spice
from astropy.utils.data import download_files_in_parallel


class ClientSPICE:
    """
    Client for fetching, caching, and managing NAIF SPICE kernels.

    This class provides a lightweight interface for:

    - Querying remote kernel sources
    - Downloading SPICE kernel files
    - Managing local kernel files
    - Temporarily loading kernels into a `spiceypy.KernelPool`

    It supports multiple kernel groups (generic, MESSENGER-specific, etc.)
    and can work with both remote and locally available kernel files.

    Attributes:
        KERNEL_LOCATIONS (dict[str, dict[str, Any]]):
            Mapping of kernel groups to their remote locations. Each entry has:

                {
                    "BASE": str,        # Base URL of the kernel repository
                    "DIRECTORY": str,   # Subdirectory path for kernel files
                    "PATTERNS": list[str]  # File patterns, '?' acts as wildcard
                }

        _query_buffer (list[str]):
            Internal buffer holding URLs of kernels resolved for download.

        _local_buffer (list[pathlib.Path]):
            Internal buffer of locally added SPICE kernel files that will
            be included when `fetch` is called.

    Example:
    ```
        client = ClientSPICE()
        client.add_local_kernels([Path("/path/to/local/kernel.bsp")])
        paths = client.fetch(check_for_updates=True)
        with client.KernelPool():
            # SPICE kernels are loaded here
            pass
    ```
    """

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
            "MESSENGER Frames (tf)": {
                "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
                "DIRECTORY": "pds/data/mess-e_v_h-spice-6-v1.0/messsp_1000/data/fk/",
                "PATTERNS": ["msgr_dyn_v600.tf"],
            },
            "MESSENGER": {
                "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
                "DIRECTORY": "pds/data/mess-e_v_h-spice-6-v1.0/messsp_1000/data/spk/",
                "PATTERNS": ["msgr_??????_??????_??????_od431sc_2.bsp"],
            },
        },
    ):
        """
        Client for fetching and storing NAIF SPICE kernels from remote sources.

        This class provides a lightweight interface for querying, downloading,
        and managing SPICE kernel files from HTTP-accessible repositories such
        as the NAIF archive.

        Args:
            KERNEL_LOCATIONS (dict[str, dict[str, Any]], optional):
                Mapping of kernel groups to their remote locations. Each entry
                should follow this structure:

                    {
                        "Arbitrary Name": {
                            "BASE": str,        # Base URL (e.g. NAIF server)
                            "DIRECTORY": str,   # Subdirectory path (e.g. "spk/", "fk/")
                            "PATTERNS": list[str],  # Filename patterns ('?' acts as wildcard)
                        }
                    }

                Default configuration includes a minimal set of MESSENGER and
                generic NAIF kernels.

        Attributes:
            KERNEL_LOCATIONS (dict[str, dict[str, Any]]):
                Configuration of kernel sources.

            _query_buffer (list[str]):
                Internal buffer of remote query results.

            _local_buffer (list[pathlib.Path]):
                Internal buffer of downloaded/local kernel file paths.
        """
        self.KERNEL_LOCATIONS = KERNEL_LOCATIONS
        self._query_buffer: list[str] = []
        self._local_buffer: list[Path] = []

    def add_local_kernels(self, paths: list[Path]) -> None:
        """
        Add local SPICE kernel files to the load buffer.

        These files will be included alongside downloaded kernels when
        `fetch` is called.

        Args:
            paths (list[pathlib.Path]):
                List of local file paths to SPICE kernels.

        Returns:
            None
        """

        self._local_buffer.extend(paths)

    def flush_local_kernel_buffer(self) -> None:
        """
        Clear the local kernel buffer.

        Removes all previously added local kernel file paths from the internal
        buffer.

        Returns:
            None
        """
        self._local_buffer: list[Path] = []

    def fetch(self, check_for_updates: bool = False) -> list[str]:
        """
        Resolve, download, and return SPICE kernel file paths.

        More info:
            1. Expands all configured kernel URL patterns.
            2. Downloads matching files (or reuses cached versions).
            3. Appends any locally buffered kernels.
            4. Clears the internal query buffer.

        Args:
            check_for_updates (bool, optional):
                If ``True``, forces revalidation or re-download of cached files.
                If ``False`` (default), cached files are reused when available.

        Returns:
            list[str]:
                List of file paths to all available kernels (downloaded and local).
        """

        all_urls: list[str] = []

        for cfg in self.KERNEL_LOCATIONS.values():
            base = cfg["BASE"]
            directory = cfg["DIRECTORY"]
            patterns = cfg["PATTERNS"]

            all_urls.extend(expand_patterns(base, directory, patterns))

        self._query_buffer.extend(all_urls)

        data_paths = download_files_in_parallel(
            self._query_buffer,
            cache="update" if check_for_updates else True,
            pkgname="hermpy",
        )

        # Return downloaded paths and anything in the local buffer.
        return data_paths + [str(p) for p in self._local_buffer]

    # We want this class to be able to function as a spiceypy.KernelPool()
    @contextmanager
    def KernelPool(self):
        """
        Context manager for temporarily loading SPICE kernels.

        This wraps `spiceypy.KernelPool`, automatically loading all
        kernels returned by `fetch` for the duration of the context.

        Yields:
            None:
                Control is yielded back to the caller while the kernel pool
                is active.

        Example
        ```
            with client.KernelPool():
                # SPICE kernels are loaded within this block
                pass

        ```
        """
        with spice.KernelPool(self.fetch()):
            yield


def list_remote_files(url: str) -> list[str]:
    with urlopen(url) as f:
        html = f.read().decode("utf-8")

    # Extract href targets
    return re.findall(r'href="([^"/]+)"', html)


def expand_patterns(base_url: str, directory: str, patterns: list[str]) -> list[str]:
    full_dir_url = base_url + directory
    files = list_remote_files(full_dir_url)

    matched = []
    for pattern in patterns:
        matched.extend(
            f"{full_dir_url}{fname}" for fname in files if fnmatch(fname, pattern)
        )

    return matched
