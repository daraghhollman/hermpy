from pathlib import Path
from typing import Sequence
from parfive import Downloader, Results


def download_files(urls: Sequence[str], max_retries: int = 3) -> Results:
    dl = Downloader()
    files: Results = dl.simple_download(urls, path=Path.home() / ".hermpy")

    retry_count = 1
    while len(files.errors) != 0:
        if retry_count >= max_retries:
            break
        print(f"Failed to download all files. Retrying ({retry_count}/{max_retries}).")
        retry_dl = Downloader(max_conn=1, max_splits=1)
        files = retry_dl.retry(files)
        retry_count += 1

    return files
