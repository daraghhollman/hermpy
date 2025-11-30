"""
Functions for loading and handling MAG data
"""

import datetime as dt
import multiprocessing
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.signal
from sunpy.time import TimeRange
from tqdm import tqdm

import hermpy.trajectory
from hermpy.utils import Constants


def _load_messenger(
    file_paths: list[Path],
    verbose=False,
    included_columns: set = set(),
    multiprocess: bool = False,
) -> pd.DataFrame:
    """Loads a list of MESSENGER MAG files and combines them into one output

    Parameters
    ----------
    file_paths : list[str]
        A list of paths to the data files to be loaded.


    Returns
    -------
    multi_file_data : pandas.DataFrame
        The combined data from each file loaded.
    """

    multi_file_data = []
    # Load and concatenate into one dataframe

    if multiprocess:
        with multiprocessing.Pool() as pool:
            for result in tqdm(
                pool.imap(_extract_data, file_paths),
                total=len(file_paths),
                desc="Extracting Data",
                disable=not verbose,
            ):
                multi_file_data.append(result[list(included_columns)])

    else:
        for path in tqdm(
            file_paths,
            total=len(file_paths),
            desc="Extracting Data",
            disable=not verbose,
        ):
            multi_file_data.append(_extract_data(path)[list(included_columns)])

    multi_file_data = pd.concat(multi_file_data)

    multi_file_data = multi_file_data.reset_index(drop=True)

    return multi_file_data


def load_between_dates(
    root_dir: Path | str,
    time_range: TimeRange,
    average: int | None = 1,
    aberrate: bool = True,
    included_columns: set = set(),
    multiprocess: bool = False,
    verbose: bool = False,
):
    """Automatically finds and loads files between a start and end point

    Automatically locally finds and loads mag data files from MESSENGER
    between a start and end point using a common regex.
    Uses `Load_Messenger`.


    Parameters
    ----------
    root_dir: str
        The base directory to search in. Expects files in the following
        format:

        root_dir/2012/01_JAN/MAGMSOSCIAVG12010_01_V08.TAB

    time_range: sunpy.time.TimeRange
        The range of times to load data between.

    average: int {1, 5, 10, 60, None}, optional
        Which time average of data product to load. i.e. 1 second average,
        5 second average, etc.

        If 'None', the unaveraged data will be downloaded.

    aberrate: bool {True, False}, optional
        Should the dataframe contain MAG data and Ephemeris data in MSM'

        Requires a loaded spice kernel

    included_columns: set, optional
        A set containing the names of the columns the user wishes to load.
        Defaults to including everything.

    Returns
    -------
    data : pandas.DataFrame
        The combined data from each file loaded between the input dates.
    """

    if isinstance(root_dir, str):
        root_dir = Path(root_dir)

    # convert start and end to days
    start_date = time_range.start.to_datetime().date()
    end_date = time_range.end.to_datetime().date()

    dates_to_load: list[dt.date] = [
        start_date + dt.timedelta(days=i)
        for i in range((end_date - start_date).days + 1)
    ]

    files_to_load: list[Path] = []
    for date in tqdm(
        dates_to_load,
        total=len(dates_to_load),
        desc="Loading Files",
        disable=not verbose,
    ):
        if average is not None:
            # Full cadence
            path = (
                root_dir / f"MAGMSOSCIAVG{date.strftime('%y%j')}_{average:02d}_V08.TAB"
            )
        else:
            # Averaged cadence
            path = root_dir / f"MAGMSOSCI{date.strftime('%y%j')}_V08.TAB"

        files_to_load.append(path)

    if included_columns == set():
        included_columns = {
            "date",
            "X MSO (radii)",
            "Y MSO (radii)",
            "Z MSO (radii)",
            "X MSM (radii)",
            "Y MSM (radii)",
            "Z MSM (radii)",
            "range (MSO)",
            "Bx",
            "By",
            "Bz",
            "|B|",
        }

    data = _load_messenger(
        files_to_load,
        verbose=verbose,
        included_columns=included_columns,
        multiprocess=multiprocess,
    )

    data = _strip_data(data, time_range)

    if aberrate:
        if verbose:
            print("Adding aberrated terms")
        data = _add_aberrated_terms(data)

    return data


def _extract_data(path: Path):
    # Read file
    data = np.genfromtxt(path)

    years = data[:, 0]
    day_of_years = data[:, 1]
    hours = data[:, 2]
    minutes = data[:, 3]
    seconds = data[:, 4]

    dates = [
        dt.datetime(int(year), 1, 1)  # Start with the first date of that year
        + dt.timedelta(  # Add time to get to the day of year and time.
            days=day_of_year - 1,
            hours=int(hour),
            minutes=int(minute),
            seconds=float(second),
        )
        for year, day_of_year, hour, minute, second in zip(
            years, day_of_years, hours, minutes, seconds
        )
    ]

    if len(data[0]) == 16:
        ephemeris = np.array([data[:, 7], data[:, 8], data[:, 9]])
        magnetic_field = np.array([data[:, 10], data[:, 11], data[:, 12]])
    else:
        ephemeris = np.array([data[:, 6], data[:, 7], data[:, 8]])
        magnetic_field = np.array([data[:, 9], data[:, 10], data[:, 11]])

    df = pd.DataFrame(
        {
            "date": dates,
            "X MSO (radii)": ephemeris[0] / Constants.MERCURY_RADIUS_KM,
            "Y MSO (radii)": ephemeris[1] / Constants.MERCURY_RADIUS_KM,
            "Z MSO (radii)": ephemeris[2] / Constants.MERCURY_RADIUS_KM,
            "X MSM (radii)": ephemeris[0] / Constants.MERCURY_RADIUS_KM,
            "Y MSM (radii)": ephemeris[1] / Constants.MERCURY_RADIUS_KM,
            "Z MSM (radii)": (ephemeris[2] / Constants.MERCURY_RADIUS_KM)
            - Constants.DIPOLE_OFFSET_RADII,
            "range (MSO)": np.sqrt(
                ephemeris[0] ** 2 + ephemeris[1] ** 2 + ephemeris[2] ** 2
            )
            / Constants.MERCURY_RADIUS_KM,
            "Bx": magnetic_field[0],
            "By": magnetic_field[1],
            "Bz": magnetic_field[2],
            "|B|": np.sqrt(
                magnetic_field[0] ** 2 + magnetic_field[1] ** 2 + magnetic_field[2] ** 2
            ),
        }
    )

    return df


def _strip_data(data: pd.DataFrame, time_range: TimeRange) -> pd.DataFrame:
    """Shortens MAG data to only include times between a start and end time

    Removes the start and end of a pandas dataframe (containing a dt.datetime "date" row)
    to match give start and end time.


    Parameters
    ----------
    data : pandas.DataFrame
        Data as a pandas dataframe, typically loaded using `Load_Messenger()`.

    time_range: sunpy.time.TimeRange
        The time range within which to keep data. Rows prior and after
        these times will be dropped.


    Returns
    -------
    stripped_data : pandas.DataFrame
        A new dataframe containing only the data between the given dates.
    """

    stripped_data = data.loc[
        data["date"].between(
            time_range.start.to_datetime(), time_range.end.to_datetime()
        )
    ]
    stripped_data = stripped_data.reset_index(drop=True)

    return stripped_data


def _remove_data_spikes(
    data: pd.DataFrame, threshold: int = 10_000, padding: int = 120
) -> None:
    """Removes non-physical large spikes in the data

    Replaces values surrounding peaks above 10,000 nT with np.nan

    Parameters
    ----------
    data : pandas.DataFrame
        Data as a pandas dataframe, typically loaded using `Load_Messenger()`.

    threshold : int {10,000}, optional
        Threshold at which to start removing values.

    padding : int {90}, optional
        The number of seconds padding on the peak of the data spike.
        From observations, no less than 60 seconds should be used here.


    Returns
    -------
    None
        Operates in place

    """

    components = ["|B|", "Bx", "By", "Bz"]

    # First find the peaks in the data
    peaks, _ = scipy.signal.find_peaks(
        data["|B|"], height=threshold, distance=padding / 2
    )

    for peak_index in peaks:
        for component in components:
            data.loc[peak_index - padding : peak_index + padding, component] = np.nan

    return


def _add_aberrated_terms(data: pd.DataFrame) -> pd.DataFrame:
    """Shift the data into the aberrated frame. MSO -> MSO', MSM -> MSM'


    The solar wind impacts mercury's magnetosphere along an axis different
    from the vector to the sun due to its orbital velocity. We define a
    coordinate system with the x axis rotated to be along this direction,
    rather than pointing at the sun. This is the 'aberrated', or 'primed'
    frame.

    This function rotates the MAG measurements and spacecraft positions
    into this frame.


    Parameters
    ----------
    data : pandas.DataFrame
        Data as a pandas dataframe, typically loaded using `Load_Messenger()`.


    Returns
    -------
    data : pandas.DataFrame
        The input data adjusted as described.
    """

    # Find only unique days
    unique_dates = data["date"].dt.floor("D").unique()
    # Precompute aberration angles as dictionary
    aberration_angles = {
        date: hermpy.trajectory.get_aberration_angle(date) for date in unique_dates
    }

    # Map aberration angles back to the dataframe
    data["Aberration Angle"] = data["date"].dt.floor("D").map(aberration_angles)

    # Get mutlipliers
    cos_terms = np.cos(data["Aberration Angle"])
    sin_terms = np.sin(data["Aberration Angle"])

    # Rotate MAG vectors
    data["Bx'"] = data["Bx"] * cos_terms - data["By"] * sin_terms
    data["By'"] = data["Bx"] * sin_terms - data["By"] * cos_terms
    data["Bz'"] = data["Bz"]

    # Rotate ephemeris coordinates in radii
    data["X MSM' (radii)"] = (
        data["X MSM (radii)"] * cos_terms - data["Y MSM (radii)"] * sin_terms
    )
    data["Y MSM' (radii)"] = (
        data["X MSM (radii)"] * sin_terms + data["Y MSM (radii)"] * cos_terms
    )
    data["Z MSM' (radii)"] = data["Z MSM (radii)"]

    return data


def aberrate(
    x: float, y: float, z: float, date: dt.datetime
) -> tuple[float, float, float]:
    """Aberrate any singular x, y, z point

    The solar wind impacts mercury's magnetosphere along an axis different
    from the vector to the sun due to its orbital velocity. We define a
    coordinate system with the x axis rotated to be along this direction,
    rather than pointing at the sun. This is the 'aberrated', or 'primed'
    frame.


    Parameters
    ----------
    data : pandas.DataFrame
        Data as a pandas dataframe, typically loaded using `Load_Messenger()`.


    Returns
    -------
    new_x: float
        Aberrated x position

    new_y: float
        Aberrated y position

    new_z: float
        Aberrated z position

    date: datetime.datetime | datetime.date
        The date to aberrate at.
    """

    aberration_angle = hermpy.trajectory.get_aberration_angle(date)

    # Adjust x and y ephemeris and data
    new_x: float = x * np.cos(aberration_angle) - y * np.sin(aberration_angle)
    new_y: float = x * np.sin(aberration_angle) + y * np.cos(aberration_angle)

    return (new_x, new_y, z)


def _chunk_dates(start_date, end_date, days_per_chunk):
    """Divide a date range into smaller chunks of a specified size in days."""
    current_start = start_date
    while current_start < end_date:
        current_end = min(current_start + dt.timedelta(days=days_per_chunk), end_date)
        yield current_start, current_end
        current_start = current_end


def save_mission(data_directory: Path, save_path: Path, days_per_chunk=60):
    mission_start = dt.datetime(2011, 3, 23, 15, 37)
    mission_end = dt.datetime(2015, 4, 30, 15, 8)

    with open(save_path, "wb") as f:
        for start_date, end_date in _chunk_dates(
            mission_start, mission_end, days_per_chunk
        ):  # Process 30 days at a time
            data_chunk = load_between_dates(
                data_directory,
                TimeRange(mission_start, mission_end),
                multiprocess=True,
            )
            _remove_data_spikes(data_chunk)

            # Reduce columns to save on both storage size,
            # and when loaded into memory.
            columns_to_include = [
                "date",
                "|B|",
                "Bx'",
                "By'",
                "Bz'",
                "X MSM' (radii)",
                "Y MSM' (radii)",
                "Z MSM' (radii)",
            ]
            data_chunk = data_chunk[columns_to_include]

            print(f"Dumped data between {start_date}, and {end_date}")
            pickle.dump(data_chunk, f)


def load_mission(path: str):
    data_chunks = []

    with open(path, "rb") as f:
        while True:
            try:
                data_chunk = pickle.load(f)
                data_chunks.append(data_chunk)

            except EOFError:  # end of file error
                break

    return pd.concat(data_chunks)
