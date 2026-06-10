import calendar
import datetime as dt
from pathlib import Path
from typing import Any

from astropy.time import Time
from sunpy.net import Scraper
from sunpy.time import TimeRange

from hermpy.utils import download_files


class ClientMESSENGER:
    """
    Client for querying and downloading MESSENGER spacecraft data from the
    NASA Planetary Data System (PDS).

    Supports multiple instruments and data products, including magnetometer
    (MAG) data at various cadences and the Fast Imaging Plasma Spectrometer
    (FIPS). Data is retrieved from the PDS Planetary Plasma Interactions
    Node and downloaded locally on request.

    :param PDS_BASE_URL: Base URL for the PDS data server.
    :param PDS_DATA_LOCATION: Mapping from instrument name to its path
        relative to ``PDS_BASE_URL``. Supported keys include ``"MAG"``,
        ``"MAG 1s"``, ``"MAG 5s"``, ``"MAG 10s"``, ``"MAG 60s"``,
        ``"MAG RTN 60s"``, and ``"FIPS"``.
    :param FILE_PATTERN: Mapping from instrument name to the filename
        pattern used by :class:`sunpy.net.Scraper` to resolve individual
        files. Patterns may contain ``{subdir}``, ``{year}``,
        ``{day_of_year}``, and ``{version}`` placeholders.

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
        _PDS_DATA_LOCATION: dict[str, Any] = {
            # MAG
            "MAG": "mess-mag-calibrated/data/mso/",
            "MAG 1s": "mess-mag-calibrated/data/mso-avg/",
            "MAG 5s": "mess-mag-calibrated/data/mso-avg/",
            "MAG 10s": "mess-mag-calibrated/data/mso-avg/",
            "MAG 60s": "mess-mag-calibrated/data/mso-avg/",
            "MAG RTN 60s": "mess-mag-calibrated/data/rtn-avg/",
            # FIPS
            "FIPS": "mess-epps-fips-calibrated/data/scan/",
        },
        _FILE_PATTERN: dict[str, str] = {
            "MAG": "{{year:4d}}/{subdir}/MAGMSOSCI{{year:2d}}{{day_of_year:3d}}_V{{version}}.TAB",
            "MAG 1s": "{{year:4d}}/{subdir}/MAGMSOSCIAVG{{year:2d}}{{day_of_year:3d}}_01_V{{version}}.TAB",
            "MAG 5s": "{{year:4d}}/{subdir}/MAGMSOSCIAVG{{year:2d}}{{day_of_year:3d}}_05_V{{version}}.TAB",
            "MAG 10s": "{{year:4d}}/{subdir}/MAGMSOSCIAVG{{year:2d}}{{day_of_year:3d}}_10_V{{version}}.TAB",
            "MAG 60s": "{{year:4d}}/{subdir}/MAGMSOSCIAVG{{year:2d}}{{day_of_year:3d}}_60_V{{version}}.TAB",
            "MAG RTN 60s": "{{year:4d}}/{subdir}/MAGRTNSCIAVG{{year:2d}}{{day_of_year:3d}}_60_V{{version}}.TAB",
            # FIPS
            "FIPS": "{{year:4d}}/{subdir}/FIPS_R{{year:4d}}{{day_of_year:3d}}CDR_V{{version}}.TAB",
        },
    ):
        # Paths defining where the data can be found
        self.PDS_BASE_URL = _PDS_BASE_URL
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

    def query(self, time_range: TimeRange, instrument: str) -> list[str]:
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
        """

        pattern = (
            f"{self.PDS_BASE_URL}{self.PDS_DATA_LOCATION[instrument]}"
            f"{self.FILE_PATTERN[instrument]}"
        )

        subdir = _get_subdir(time_range)

        if isinstance(subdir, list):
            urls: list[Any] = []
            for s in subdir:
                pattern_kwargs = {
                    "subdir": s,
                }

                scraper = Scraper(format=pattern, **pattern_kwargs)
                filelist = scraper.filelist(time_range)
                assert type(filelist) is list
                urls.extend(filelist)

        else:
            pattern_kwargs = {
                "subdir": subdir,
            }

            scraper = Scraper(format=pattern, **pattern_kwargs)
            filelist = scraper.filelist(time_range)
            assert type(filelist) is list
            urls = filelist

        # For some reason, this gives us more than just the files we want.
        # We need to get a list of all the day of years in our time range
        # and compare.
        doys = _get_timerange_doys(time_range)
        urls = [url for url in urls if any(doy in url.split("/")[-1] for doy in doys)]

        # Add urls to search buffer
        self._query_buffer.extend(urls)

        return urls

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


def _get_subdir(time_range: TimeRange) -> str | list[str]:
    """
    Determine the MAG subdirectories required for a given time range.
    """

    # We only need to work with the dates
    start_date = time_range.start.datetime.date()
    end_date = time_range.end.datetime.date()

    # We need to work month by month for the time range:
    subdirs: list[str] = []

    month_start_date = dt.date(start_date.year, start_date.month, 1)

    while month_start_date <= end_date:
        year, month = month_start_date.year, month_start_date.month

        first_day = dt.date(year, month, 1)
        last_day = dt.date(year, month, calendar.monthrange(year, month)[1])

        start_doy = first_day.timetuple().tm_yday
        end_doy = last_day.timetuple().tm_yday

        month_str = calendar.month_abbr[month].upper()

        subdirs.append(f"{start_doy:03d}_{end_doy:03d}_{month_str}")

        # Advance to next month
        if month == 12:
            month_start_date = dt.date(year + 1, 1, 1)
        else:
            month_start_date = dt.date(year, month + 1, 1)

    return subdirs[0] if len(subdirs) == 1 else subdirs


def _get_timerange_doys(time_range: TimeRange) -> list[int]:
    """
    For a given TimeRange return the day-of-years it spans. Can result in a
    list of length one, this is wanted behaviour.
    """

    dates: list[Time] = time_range.get_dates()

    doys = [date.strftime("%j") for date in dates]

    return doys
