"""
Functions for loading and handling MAG data
"""

import datetime as dt
import multiprocessing
import warnings
from glob import glob

import numpy as np
import pandas as pd
from tqdm import tqdm

import hermpy.trajectory as trajectory
from hermpy.utils import Constants


def Load_Messenger(file_paths: list[str], verbose=False) -> pd.DataFrame:
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
    # Load and concatonate into one dataframe

    with multiprocessing.Pool() as pool:
        for result in tqdm(pool.imap(Extract_Data, file_paths), total=len(file_paths), desc="Extracting Data", disable=not verbose):
            multi_file_data.append(result)

    multi_file_data = pd.concat(multi_file_data)

    multi_file_data = multi_file_data.reset_index(drop=True)

    return multi_file_data


def Load_Between_Dates(
    root_dir: str,
    start: dt.datetime,
    end: dt.datetime,
    average: int = 1,
    strip: bool = True,
    aberrate: bool = True,
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

    start : datetime.datetime
        The start point of the data search

    end : datetime.datetime
        The end point of the data search

    average : int {1, 5, 10, 60}, optional
        Which time average of data product to load. i.e. 1 second average,
        5 second average, etc.

    strip : bool {True, False}, optional
        Should the data be shortened to match the times in start and end

    aberrate : bool {True, False}, optional
        Should the dataframe contain MAG data and Ephemeris data in MSM'

        Requires a loaded spice kernel

    Returns
    -------
    data : pandas.DataFrame
        The combined data from each file loaded between the input dates.
    """

    # convert start and end to days
    start_date = start.date()
    end_date = end.date()

    dates_to_load: list[dt.date] = [
        start_date + dt.timedelta(days=i)
        for i in range((end_date - start_date).days + 1)
    ]

    files_to_load: list[str] = []
    for date in tqdm(dates_to_load, total=len(dates_to_load), desc="Loading Files", disable= not verbose):
        file: list[str] = glob(
            root_dir
            + f"{date.strftime('%Y')}/*/MAGMSOSCIAVG{date.strftime('%y%j')}_{average:02d}_V08.TAB"
        )

        if len(file) > 1:
            raise ValueError("ERROR: There are duplicate data files being loaded.")
        elif len(file) == 0:
            warnings.warn(f"WARNING: The data trying to be loaded doesn't exist at filepath: {f'{date.strftime('%Y')}/*/MAGMSOSCIAVG{date.strftime('%y%j')}_{average:02d}_V08.TAB'}")
            continue

        files_to_load.append(file[0])

    data = Load_Messenger(files_to_load, verbose=verbose)

    if strip:
        data = Strip_Data(data, start, end)

    if aberrate:
        if verbose:
            print("Adding aberrated terms")
        data = Add_Aberrated_Terms(data)

    return data

def Extract_Data(path):
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
            seconds=int(second),
        )
        for year, day_of_year, hour, minute, second in zip(
            years, day_of_years, hours, minutes, seconds
        )
    ]

    ephemeris = np.array([data[:, 7], data[:, 8], data[:, 9]])
    magnetic_field = np.array([data[:, 10], data[:, 11], data[:, 12]])

    df = pd.DataFrame(
        {
            "date": dates,
            "X MSO (km)": ephemeris[0],
            "Y MSO (km)": ephemeris[1],
            "Z MSO (km)": ephemeris[2],

            "X MSO (radii)": ephemeris[0] / Constants.MERCURY_RADIUS_KM,
            "Y MSO (radii)": ephemeris[1] / Constants.MERCURY_RADIUS_KM,
            "Z MSO (radii)": ephemeris[2] / Constants.MERCURY_RADIUS_KM,

            "X MSM (km)": ephemeris[0],
            "Y MSM (km)": ephemeris[1],
            "Z MSM (km)": ephemeris[2] - Constants.DIPOLE_OFFSET_KM,

            "X MSM (radii)": ephemeris[0] / Constants.MERCURY_RADIUS_KM,
            "Y MSM (radii)": ephemeris[1] / Constants.MERCURY_RADIUS_KM,
            "Z MSM (radii)": (ephemeris[2] / Constants.MERCURY_RADIUS_KM) - Constants.DIPOLE_OFFSET_RADII,

            "range (MSO)": np.sqrt(
                ephemeris[0] ** 2 + ephemeris[1] ** 2 + ephemeris[2] ** 2
            ) / Constants.MERCURY_RADIUS_KM,

            "Bx": magnetic_field[0],
            "By": magnetic_field[1],
            "Bz": magnetic_field[2],
            "|B|": np.sqrt( magnetic_field[0] ** 2
                   + magnetic_field[1] ** 2
                   + magnetic_field[2] ** 2),
        }
    )

    return df

def Strip_Data(
    data: pd.DataFrame, start: dt.datetime, end: dt.datetime
) -> pd.DataFrame:
    """Shortens MAG data to only include times between a start and end time

    Removes the start and end of a pandas dataframe (containing a dt.datetime "date" row)
    to match give start and end time.


    Parameters
    ----------
    data : pandas.DataFrame
        Data as a pandas dataframe, typically loaded using `Load_Messenger()`.

    start : datetime.datetime
        The start date of the data to be kept. All rows prior will be removed.

    end : datetime.datetime
        The end date of the data to be kept. All rows after will be removed.


    Returns
    -------
    stripped_data : pandas.DataFrame
        A new dataframe containing only the data between the given dates.
    """

    stripped_data = data.loc[data["date"].between(start, end)]
    stripped_data = stripped_data.reset_index(drop=True)

    return stripped_data


def Remove_Spikes(data: pd.DataFrame, threshold: int = 1_000) -> None:
    """Removes non-physical large spikes (> 1 μT) in the data

    Replaces values above 1,000 nT with np.nan

    Parameters
    ----------
    data : pandas.DataFrame
        Data as a pandas dataframe, typically loaded using `Load_Messenger()`.

    threshold : float {1,000} optional,
        Threshold at which to start removing values.


    Returns
    -------
    None
        Operates in place

    """

    components = ["|B|", "Bx", "By", "Bz"]

    for component in components:

        data.loc[abs(data[component]) > threshold, component] = np.nan

    return


def Determine_Variability(items):
    data, row, time_frame = items

    # Get the rows before and after
    data_to_average = data.loc[
        (data["date"].between(row["date"] - time_frame, row["date"]))
        | (data["date"].between(row["date"], row["date"] + time_frame))
    ]["|B|"]

    average_mag = np.mean(data_to_average)
    variability = np.sqrt((row["|B|"] - average_mag) ** 2)

    return variability


def Add_Field_Variability(
    data: pd.DataFrame, time_frame: dt.timedelta, multiprocess=False
):

    if multiprocess:
        variabilities = []
        count = 0
        items = [(data, row, time_frame) for _, row in data.iterrows()]
        with multiprocessing.Pool() as pool:
            for result in pool.imap(Determine_Variability, items):
                if result != None:
                    variabilities.append(result)
                count += 1
                print(f"{count} / {len(data)}", end="\r")

    else:
        print("Adding Field Variability")
        variabilities = []
        for i, row in tqdm(data.iterrows(), total=len(data)):

            # Get the rows before and after
            data_to_average = data.loc[
                (data["date"].between(row["date"] - time_frame, row["date"]))
                | (data["date"].between(row["date"], row["date"] + time_frame))
            ]["|B|"]

            average_mag = np.mean(data_to_average)
            variability = np.sqrt((row["|B|"] - average_mag) ** 2)

            variabilities.append(variability)

    data.insert(len(data.columns), "B_variability", variabilities)

    return data


def Add_Aberrated_Terms(data: pd.DataFrame) -> pd.DataFrame:
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
    aberration_angles = {date: trajectory.Get_Aberration_Angle(date) for date in unique_dates}
    
    # Map aberration angles back to the dataframe
    data["Aberration Angle"] = data["date"].dt.floor("D").map(aberration_angles)

    # Get mutlipliers
    cos_terms = np.cos(data["Aberration Angle"])
    sin_terms = np.sin(data["Aberration Angle"])

    # Rotate MAG vectors
    data["Bx'"] = data["Bx"] * cos_terms - data["By"] * sin_terms
    data["By'"] = data["Bx"] * sin_terms - data["By"] * cos_terms
    data["Bz'"] = data["Bz"]

    # Rotate ephemeris coordinates in kilometers
    data["X MSM' (km)"] = data["X MSM (km)"] * cos_terms - data["Y MSM (km)"] * sin_terms
    data["Y MSM' (km)"] = data["X MSM (km)"] * sin_terms + data["Y MSM (km)"] * cos_terms
    data["Z MSM' (km)"] = data["Z MSM (km)"]

    # Rotate ephemeris coordinates in radii
    data["X MSM' (radii)"] = data["X MSM (radii)"] * cos_terms - data["Y MSM (radii)"] * sin_terms
    data["Y MSM' (radii)"] = data["X MSM (radii)"] * sin_terms + data["Y MSM (radii)"] * cos_terms
    data["Z MSM' (radii)"] = data["Z MSM (radii)"]

    return data


def Aberrate(
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

    aberration_angle = trajectory.Get_Aberration_Angle(date)

    # Adjust x and y ephemeris and data
    new_x: float = x * np.cos(aberration_angle) - y * np.sin(aberration_angle)
    new_y: float = x * np.sin(aberration_angle) + y * np.cos(aberration_angle)

    return (new_x, new_y, z)


def Convert_To_Polars(data: pd.DataFrame) -> pd.DataFrame:
    """Converts data from cartesian to polar coordinates

    Convets to polar coordinates irrespective of frame.
    Perform transformations and aberrations prior to this
    function.

    Takes the values for x, y, and z and creates a new column
    for each polar coordinate.


    Parameters
    ----------
    data : pandas.DataFrame
        A dataframe of data to be converted


    Returns
    -------
    out: pandas.DataFrame
        The resulting data with added columns
        [mag_r, mag_theta, mag_phi]

    """

    x = data["Bx"]
    y = data["By"]
    z = data["Bz"]

    r = np.sqrt(x**2 + y**2 + z**2)
    theta = Constants.RADIANS_TO_DEGREES(np.arctan2(y, x))
    phi = Constants.RADIANS_TO_DEGREES(np.arctan2(z, r))

    data["Br"] = r
    data["Btheta"] = theta
    data["Bphi"] = phi

    return data
