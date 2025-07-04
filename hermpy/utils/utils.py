import datetime as dt
import multiprocessing
import os

import numpy as np
import requests
from tqdm import tqdm


class User:

    METAKERNEL = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"
    DATA_DIRECTORIES = {
        "MAG": "/home/daraghhollman/Main/data/mercury/messenger/mag/avg_1_second/",
        "MAG_FULL": "/home/daraghhollman/Main/data/mercury/messenger/mag/full_cadence/",
        "FIPS": "/home/daraghhollman/Main/data/mercury/messenger/FIPS/",
        "FULL MISSION": "/home/daraghhollman/Main/data/mercury/messenger_mag",
    }
    CROSSING_LISTS = {
        "Philpott": "/home/daraghhollman/Main/Work/mercury/DataSets/philpott_2020.xlsx",
        "Sun": "/home/daraghhollman/Main/Work/mercury/DataSets/sun_crossing_lists/",
    }


class Constants:
    # If no units are specified in the variable name,
    # SI units are implied.
    MERCURY_RADIUS = 2_439_700  # meters
    MERCURY_RADIUS_KM = MERCURY_RADIUS / 1_000  # kilometers

    DIPOLE_OFFSET_KM = 479  # km
    DIPOLE_OFFSET_RADII = 479 / MERCURY_RADIUS_KM  # radii

    MERCURY_SEMI_MAJOR_AXIS = 57_909_050 * 1_000  # meters
    SOLAR_MASS = 1.9891e30  # kilograms

    SOLAR_WIND_SPEED_AVG = 400_000  # meters / second

    G = 6.6743e-11  # N m^2 / kg^2

    @staticmethod
    def KM_TO_AU(km):
        return km / 1.496e8

    @staticmethod
    def RADIANS_TO_DEGREES(radians):
        return np.degrees(radians)

    @staticmethod
    def DEGREES_TO_RADIANS(degrees):
        radians = degrees * np.pi / 180
        return radians


class Urls:

    PDS_BASE = "https://search-pdsppi.igpp.ucla.edu/"
    MAG_EXTENSION_AVG = "ditdos/download?id=pds://PPI/mess-mag-calibrated/data/mso-avg/"
    MAG_EXTENSION = "ditdos/download?id=pds://PPI/mess-mag-calibrated/data/mso/"


def Download_MESSENGER_MAG(
    save_directory: str = User.DATA_DIRECTORIES["MAG"],
    resolution: str | None = "01",
) -> None:
    """Function to automatically download MESSENGER MAG data


    Parameters
    ----------
    save_directory : str
        Directory to save MAG files to.

    force_update : bool {False, True}, optional
        Default behaviour is to only update files if they have changed.
        Update can be forced.

    show_progress : bool {True, False}, optional
        Shows a progress bar to track downloads.


    Returns
    -------
    None

    """

    if resolution is not None:
        base_url = Urls.PDS_BASE + Urls.MAG_EXTENSION_AVG

    else:
        base_url = Urls.PDS_BASE + Urls.MAG_EXTENSION

    urls = []
    download_locations = []

    for year in [2011, 2012, 2013, 2014, 2015]:

        for month_index in range(1, 13):

            if year == 2011 and month_index < 4:
                continue

            # First day of the month
            first_day = dt.date(year, month_index, 1)

            # Last day of the month
            if month_index == 12:
                last_day = dt.date(year + 1, 1, 1) - dt.timedelta(days=1)

            else:
                last_day = dt.date(year, month_index + 1, 1) - dt.timedelta(days=1)

            current_day = first_day
            while current_day <= last_day:

                if resolution is not None:
                    file_format = (
                        f"{year}/"
                        + f"{first_day.strftime('%j')}_{last_day.strftime('%j')}_{first_day.strftime('%b').upper()}/"
                        + f"MAGMSOSCIAVG{current_day.strftime('%y%j')}_{resolution}_V08.TAB"
                    )

                else:
                    file_format = (
                        f"{year}/"
                        + f"{first_day.strftime('%j')}_{last_day.strftime('%j')}_{first_day.strftime('%b').upper()}/"
                        + f"MAGMSOSCI{current_day.strftime('%y%j')}_V08.TAB"
                    )

                urls.append(base_url + file_format)
                download_locations.append(save_directory + file_format)

                current_day += dt.timedelta(days=1)

    Download_In_Parallel(list(zip(urls, download_locations)))


def Download_Url(args):

    url, download_location = args

    directory = os.path.dirname(download_location)
    if not os.path.isdir(directory):
        os.makedirs(directory, exist_ok=True)

    response = requests.get(url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        with open(download_location, "wb") as file:
            file.write(response.content)

    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")

    return


def Download_In_Parallel(args):

    cpus = multiprocessing.cpu_count()

    with multiprocessing.Pool(cpus) as pool:

        for _ in tqdm(
            pool.imap_unordered(Download_Url, args),
            total=len(args),
            desc="Downloading MESSENGER MAG",
        ):
            continue
