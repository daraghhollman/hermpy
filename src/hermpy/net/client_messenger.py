import calendar
import datetime as dt
import json
import socket
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from sunpy.net import Scraper
from sunpy.time import TimeRange

from hermpy.utils import download_files

# Where cached directory listings are stored (alongside the downloaded files)
QUERY_CACHE_DIR = Path.home() / ".hermpy" / "cache" / "queries/"


class ClientMESSENGER:
    """
    Client for querying and downloading MESSENGER spacecraft data from the
    NASA Planetary Data System (PDS).

    Supports multiple instruments and data products, including magnetometer
    (MAG) data at various cadences and the Fast Imaging Plasma Spectrometer
    (FIPS). Data is retrieved from the PDS Planetary Plasma Interactions
    Node and downloaded locally on request.

    :param PDS_BASE_URL: Base URL for the PDS data server.
    :param PDS_DATA_LOCATION: Mapping from instrument name to its path relative to ``PDS_BASE_URL``.
    :param FILE_PATTERN: Mapping from instrument name to the filename pattern used by :class:`sunpy.net.Scraper` to resolve individual files.

    Example usage::

        from sunpy.time import TimeRange
        client = ClientMESSENGER()
        time_range = TimeRange("2012-01-01", "2012-01-02")
        urls = client.query(time_range, "MAG 1s")
        files = client.fetch()
    """

    def __init__(
        self,
        _PDS_BASE_URL: str = "https://pds-ppi.igpp.ucla.edu/data/",
        _PDS_DATA_LOCATION: dict[str, Any] | None = None,
        _FILE_PATTERN: dict[str, str] | None = None,
    ):
        # Paths defining where the data can be found
        self.PDS_BASE_URL = _PDS_BASE_URL

        if _PDS_DATA_LOCATION is None:
            _PDS_DATA_LOCATION = {
                "MAG": "mess-mag-calibrated/data/mso/",
                "MAG 1s": "mess-mag-calibrated/data/mso-avg/",
                "MAG 5s": "mess-mag-calibrated/data/mso-avg/",
                "MAG 10s": "mess-mag-calibrated/data/mso-avg/",
                "MAG 60s": "mess-mag-calibrated/data/mso-avg/",
                "MAG RTN 60s": "mess-mag-calibrated/data/rtn-avg/",
                # FIPS
                "FIPS": "mess-epps-fips-calibrated/data/scan/",
            }

        if _FILE_PATTERN is None:
            _FILE_PATTERN = {
                "MAG": "{{year:4d}}/{subdir}/MAGMSOSCI{{year:2d}}{{day_of_year:3d}}_V{{version}}.TAB",
                "MAG 1s": "{{year:4d}}/{subdir}/MAGMSOSCIAVG{{year:2d}}{{day_of_year:3d}}_01_V{{version}}.TAB",
                "MAG 5s": "{{year:4d}}/{subdir}/MAGMSOSCIAVG{{year:2d}}{{day_of_year:3d}}_05_V{{version}}.TAB",
                "MAG 10s": "{{year:4d}}/{subdir}/MAGMSOSCIAVG{{year:2d}}{{day_of_year:3d}}_10_V{{version}}.TAB",
                "MAG 60s": "{{year:4d}}/{subdir}/MAGMSOSCIAVG{{year:2d}}{{day_of_year:3d}}_60_V{{version}}.TAB",
                "MAG RTN 60s": "{{year:4d}}/{subdir}/MAGRTNSCIAVG{{year:2d}}{{day_of_year:3d}}_60_V{{version}}.TAB",
                # FIPS
                "FIPS": "{{year:4d}}/{subdir}/FIPS_R{{year:4d}}{{day_of_year:3d}}CDR_V{{version}}.TAB",
            }

        self.PDS_DATA_LOCATION = _PDS_DATA_LOCATION
        self.FILE_PATTERN = _FILE_PATTERN

        # We want the user to be able to query for the existance of
        # files before downloading, so we introduce a search buffer to
        # hold the results of the most recent query.
        self._query_buffer: list[str] = []

    @property
    def instruments(self) -> list[str]:
        """
        The instrument names supported by this client.

        Derived from the keys of ``PDS_DATA_LOCATION``.
        """

        return list(self.PDS_DATA_LOCATION.keys())

    def query(
        self,
        time_range: TimeRange,
        instrument: str,
        timeout: float = 60,
        retries: int = 3,
        use_cache: bool = True,
    ) -> list[str]:
        """
        Query the PDS for available files for a given instrument and time range.

        Resolves the appropriate monthly subdirectory structure, uses
        :class:`sunpy.net.Scraper` to build candidate URLs, and filters
        the results to only those matching the day-of-year values spanned
        by ``time_range``. Matched URLs are appended to the internal query
        buffer, making them available to :meth:`fetch`.

        :param time_range: The time range over which to search for data.
        :param instrument: The instrument to query. Must be one of the keys
            in :attr:`instruments`.
        :raises KeyError: If ``instrument`` is not a recognised key.
        :param timeout: How many seconds to wait before raising a timeout error
        :param retries: How many times to retry a download before giving up
        :use_cache: We cache urls while scraping, which can be used later during redownloads
        """

        pattern = (
            f"{self.PDS_BASE_URL}{self.PDS_DATA_LOCATION[instrument]}"
            f"{self.FILE_PATTERN[instrument]}"
        )

        urls: list[str] = []

        previous_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)

        try:
            for subdir, chunk in _get_month_chunks(time_range):
                urls.extend(
                    self._list_chunk(
                        pattern, instrument, subdir, chunk, retries, use_cache
                    )
                )
        finally:
            socket.setdefaulttimeout(previous_timeout)

        # Add urls to search buffer
        self._query_buffer.extend(urls)

        return urls

    def _list_chunk(
        self,
        pattern: str,
        instrument: str,
        subdir: str,
        chunk: TimeRange,
        retries: int,
        use_cache: bool,
    ) -> list[str]:
        """
        List the files for a single month (one directory), with caching and
        retries.
        """

        start = chunk.start.datetime.strftime("%Y%m%d")
        end = chunk.end.datetime.strftime("%Y%m%d")
        cache_file = (
            QUERY_CACHE_DIR / f"{instrument.replace(' ', '-')}-{start}-{end}.json"
        )

        if use_cache and cache_file.exists():
            try:
                return json.loads(cache_file.read_text())
            except (json.JSONDecodeError, OSError):
                pass  # Corrupt cache entry, just re-query

        file_list: list[str] = []
        for attempt in range(1, retries + 1):
            try:
                scraper = Scraper(format=pattern, subdir=subdir)
                result = scraper.filelist(chunk)

                assert isinstance(result, list)

                file_list = _filter_to_range(result, chunk)

                break

            except OSError as e:  # includes TimeoutError and URLError
                if attempt == retries:
                    raise
                print(
                    f"Query for {subdir} ({start}) failed "
                    f"(attempt {attempt}/{retries}): {e}. Retrying..."
                )
                time.sleep(5 * attempt)

        # Only cache non-empty results, so a transient failure that returned
        # nothing doesn't get remembered.
        if use_cache and file_list:
            QUERY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps(file_list))

        return file_list

    def fetch(self) -> list[Path]:
        """
        Download all files currently held in the query buffer.

        Files that have already been downloaded locally are retrieved from
        disk rather than re-downloaded. Clears the query buffer after
        completion, so subsequent calls to :meth:`fetch` without an
        intervening :meth:`query` will return an empty list.
        """

        files = download_files(self._query_buffer)

        # Flush query buffer
        self._query_buffer = []

        return files


def _get_month_chunks(time_range: TimeRange) -> Iterator[tuple[str, TimeRange]]:
    """
    Split a time range into calendar months. For each month yield the PDS
    subdirectory name (e.g. "214_244_AUG") and a TimeRange clipped to that
    month and to the requested range.

    Subdirectory names depend on the year (leap years shift the day-of-year
    numbers), so each name is only valid for the month it was built from.
    """

    start_date = time_range.start.datetime.date()
    end_date = time_range.end.datetime.date()

    month_start = dt.date(start_date.year, start_date.month, 1)

    while month_start <= end_date:
        year, month = month_start.year, month_start.month
        month_end = dt.date(year, month, calendar.monthrange(year, month)[1])

        start_doy = month_start.timetuple().tm_yday
        end_doy = month_end.timetuple().tm_yday
        month_str = calendar.month_abbr[month].upper()
        subdir = f"{start_doy:03d}_{end_doy:03d}_{month_str}"

        chunk = TimeRange(
            max(month_start, start_date).isoformat(),
            min(month_end, end_date).isoformat(),
        )

        yield subdir, chunk

        # Advance to the first day of the next month
        month_start = dt.date(year + (month == 12), month % 12 + 1, 1)


def _filter_to_range(urls: list[str], time_range: TimeRange) -> list[str]:
    """
    Keep only URLs whose filename date falls within time_range.

    The Scraper returns every file in each directory it visits, so we filter
    on year + day-of-year (YYDDD or YYYYDDD) in the filename.
    """

    keys: set[str] = set()
    for date in time_range.get_dates():
        keys.add(date.strftime("%y%j"))  # e.g. 11152
        keys.add(date.strftime("%Y%j"))  # e.g. 2011152

    return [u for u in urls if any(k in u.split("/")[-1] for k in keys)]
