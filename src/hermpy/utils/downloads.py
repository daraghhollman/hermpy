"""
Downloading utilities for hermpy.

Provides cross-platform parallel downloading with caching and progress
tracking.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlopen

from tqdm import tqdm

from hermpy.utils.os import get_multiprocessing_start_method


@dataclass
class DownloadRequest:
    url: str
    destination: Path


def _get_file_size(url: str) -> tuple[str, int]:
    """
    Get the file size from a URL using Content-Length header.

    Parameters
    ----------
    url : str
        The URL to check.

    Returns
    -------
    tuple[str, int]
        A tuple of (url, file_size_in_bytes). Returns -1 if size cannot be determined.

    Raises
    ------
    URLError
        If the request fails.
    """
    try:
        response = urlopen(url)
        size = response.headers.get("content-length")
        if size:
            return (url, int(size))
        else:
            return (url, -1)
    except Exception:
        return (url, -1)


def _download_single_file(request: DownloadRequest) -> Path:
    """
    Download a single file from a URL to a destination path.

    This is designed to be called in parallel via multiprocessing.

    Parameters
    ----------
    request : DownloadRequest
        Download request with url and destination path.

    Returns
    -------
    Path
        The destination path where the file was saved.

    Raises
    ------
    URLError
        If the download fails.
    OSError
        If there are file system errors.
    """

    url = request.url
    destination = request.destination

    try:
        with urlopen(url) as response:
            # Create parent directory if it doesn't exist
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Download to a temporary file first, then move to final location
            temp_path = destination.with_suffix(destination.suffix + ".tmp")

            with open(temp_path, "wb") as f:
                while True:
                    chunk = response.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    f.write(chunk)

            temp_path.replace(destination)

    except Exception:
        # Clean up temp file if it exists
        temp_path = destination.with_suffix(destination.suffix + ".tmp")
        if temp_path.exists():
            temp_path.unlink()
        raise

    return destination


def download_files(
    urls: list[str],
    cache_dir: Path | None = None,
    check_for_updates: bool = False,
    num_workers: int | None = None,
    show_progress: bool = True,
) -> list[Path]:
    """
    Download files from URLs with caching and parallel processing.

    Files are cached in the specified cache directory. If a file already exists
    in the cache, it will be returned without re-downloading (unless
    check_for_updates is True).

    Parameters
    ----------
    urls : list[str]
        List of URLs to download.
    cache_dir : Path, optional
        Directory to cache downloaded files. Defaults to ~/.hermpy.
    check_for_updates : bool, optional
        If True, re-download files even if they exist in cache. Default is False.
    num_workers : int, optional
        Number of parallel workers for downloads. If None, uses CPU count.
    show_progress : bool, optional
        If True, show a progress bar using tqdm. Default is True.

    Returns
    -------
    list[Path]
        List of Path objects pointing to the downloaded/cached files.

    Raises
    ------
    URLError
        If a download fails.
    OSError
        If there are file system errors.

    Examples
    --------
    >>> urls = ["https://example.com/file1.dat", "https://example.com/file2.dat"]
    >>> paths = download_files(urls)
    >>> print(paths)
    [PosixPath('/home/user/.hermpy/file1.dat'), PosixPath('/home/user/.hermpy/file2.dat')]
    """
    if cache_dir is None:
        cache_dir = Path.home() / ".hermpy"

    cache_dir = Path(cache_dir)

    # Prepare download tasks: (url, destination_path) tuples
    download_tasks = []
    file_paths = []

    for url in urls:
        # Extract filename from URL
        filename = url.split("/")[-1]
        destination = cache_dir / filename

        file_paths.append(destination)

        # Only add to download tasks if:
        # 1. File doesn't exist, OR
        # 2. check_for_updates is True
        if not destination.exists() or check_for_updates:
            download_tasks.append(DownloadRequest(url, destination))

    # If there's nothing to download, return cached files
    if not download_tasks:
        return file_paths

    # Determine number of workers
    if num_workers is None:
        num_workers = os.cpu_count() or 1

    # Set up the context for multiprocessing based on OS
    ctx = __import__("multiprocessing").get_context(get_multiprocessing_start_method())

    # Create progress bar
    pbar = tqdm(
        total=len(download_tasks),
        disable=not show_progress,
        desc="Downloading",
        unit="file",
    )

    def update_progress(*args):
        """Callback for completed downloads."""
        pbar.update(1)

    def handle_error(exc):
        """Error callback for failed downloads."""
        pbar.close()
        raise exc

    try:
        # Use multiprocessing pool for parallel downloads
        with ctx.Pool(processes=num_workers) as pool:
            # Map the download function with async callbacks for progress
            results = []
            for task in download_tasks:
                result = pool.apply_async(
                    _download_single_file,
                    (task,),
                    callback=update_progress,
                    error_callback=handle_error,
                )
                results.append(result)

            # Wait for all downloads to complete
            for result in results:
                result.wait()
                # Check if there was an error
                if not result.successful():
                    pbar.close()
                    result.get()  # This will raise the exception

        pbar.close()

    except Exception:
        pbar.close()
        raise

    return file_paths
