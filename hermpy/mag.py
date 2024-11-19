"""
Functions for loading and handling MAG data
"""

import datetime as dt
import multiprocessing
from glob import glob

import numpy as np
import pandas as pd
from tqdm import tqdm

import hermpy.trajectory as trajectory
from hermpy.utils import Constants


def Load_Messenger(file_paths: list[str], verbose=False) -> pd.DataFrame:
    """Loads a list of MESSENGER MAG files and combines them into one output

    Reads data from a list of file paths and converts to a pandas dataframe
    with the following columns:
        date,
        hour,
        minute,
        second,
        frame,
        eph_x,
        eph_y,
        eph_z,
        range,
        mag_x,
        mag_y,
        mag_z,
        mag_total

    This function is only valid for the 1 second average data-set due to a
    format difference in the data files between different data-sets.


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
    if verbose:
        print("Loading Data")
    for path in tqdm(file_paths, total=len(file_paths), disable=not verbose):
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

        dataframe = pd.DataFrame(
            {
                "date": dates,
                "X MSM (radii)": ephemeris[0] / Constants.MERCURY_RADIUS_KM,
                "Y MSM (radii)": ephemeris[1] / Constants.MERCURY_RADIUS_KM,
                "Z MSM (radii)": ephemeris[2] / Constants.MERCURY_RADIUS_KM,
                "range (MSO)": np.sqrt(
                    ephemeris[0] ** 2 + ephemeris[1] ** 2 + ephemeris[2] ** 2
                )
                / Constants.MERCURY_RADIUS_KM,
                "Bx": magnetic_field[0],
                "By": magnetic_field[1],
                "Bz": magnetic_field[2],
                "|B|": np.sqrt(
                    magnetic_field[0] ** 2
                    + magnetic_field[1] ** 2
                    + magnetic_field[2] ** 2
                ),
            }
        )

        multi_file_data.append(dataframe)

    multi_file_data = pd.concat(multi_file_data)

    multi_file_data = multi_file_data.reset_index(drop=True)

    return multi_file_data


def Load_Between_Dates(
    root_dir: str,
    start: dt.datetime,
    end: dt.datetime,
    average: int = 1,
    strip: bool = True,
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
    for date in dates_to_load:
        file: list[str] = glob(
            root_dir
            + f"{date.strftime('%Y')}/*/MAGMSOSCIAVG{date.strftime('%y%j')}_{average:02d}_V08.TAB"
        )

        if len(file) > 1:
            raise ValueError("ERROR: There are duplicate data files being loaded.")
        elif len(file) == 0:
            raise ValueError("ERROR: The data trying to be loaded doesn't exist!")

        files_to_load.append(file[0])

    if verbose:
        print("Loading Files")

    data = Load_Messenger(files_to_load, verbose=verbose)

    if strip:
        data = Strip_Data(data, start, end)

    return data


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


def Determine_Variability(items):
    data, row, time_frame = items

    # Get the rows before and after
    data_to_average = data.loc[
        (data["date"].between(row["date"] - time_frame, row["date"]))
        | (data["date"].between(row["date"], row["date"] + time_frame))
    ]["mag_total"]

    average_mag = np.mean(data_to_average)
    variability = np.sqrt((row["mag_total"] - average_mag) ** 2)

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
            ]["mag_total"]

            average_mag = np.mean(data_to_average)
            variability = np.sqrt((row["mag_total"] - average_mag) ** 2)

            variabilities.append(variability)

    data.insert(len(data.columns), "mag_variability", variabilities)

    return data


def Adjust_For_Aberration(data: pd.DataFrame) -> pd.DataFrame:
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

    new_eph_x = []
    new_eph_y = []

    new_mag_x = []
    new_mag_y = []

    r = 0
    aberration_angle = 0
    previous_date = dt.datetime(2010, 1, 1)
    for _, row in data.iterrows():

        # check if day has changed and then update mercury distance
        if (row["date"] - previous_date) > dt.timedelta(days=1):
            r = trajectory.Get_Heliocentric_Distance(row["date"])
            previous_date = row["date"]

            # determine mercury velocity
            a = Constants.MERCURY_SEMI_MAJOR_AXIS
            M = Constants.SOLAR_MASS
            G = Constants.G

            orbital_velocity = np.sqrt(G * M * ((2 / r) - (1 / a)))
            aberration_angle = np.arctan(orbital_velocity / 400000)

        # Adjust x and y ephemeris and data
        new_mag = (
            row["mag_x"] * np.cos(aberration_angle)
            - row["mag_y"] * np.sin(aberration_angle),
            row["mag_x"] * np.sin(aberration_angle)
            + row["mag_y"] * np.cos(aberration_angle),
        )

        new_ephem = (
            row["eph_x"] * np.cos(aberration_angle)
            - row["eph_y"] * np.sin(aberration_angle),
            row["eph_x"] * np.sin(aberration_angle)
            + row["eph_y"] * np.cos(aberration_angle),
        )

        new_eph_x.append(new_ephem[0])
        new_eph_y.append(new_ephem[1])

        new_mag_x.append(new_mag[0])
        new_mag_y.append(new_mag[1])

    data["eph_x"] = new_eph_x
    data["eph_y"] = new_eph_y
    data["mag_x"] = new_mag_x
    data["mag_y"] = new_mag_y

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

    r = trajectory.Get_Heliocentric_Distance(date)

    # determine mercury velocity
    a = Constants.MERCURY_SEMI_MAJOR_AXIS
    M = Constants.SOLAR_MASS
    G = Constants.G

    orbital_velocity = np.sqrt(G * M * ((2 / r) - (1 / a)))
    aberration_angle = np.arctan(orbital_velocity / Constants.SOLAR_WIND_SPEED_AVG)

    # Adjust x and y ephemeris and data
    new_x: float = x * np.cos(aberration_angle) - y * np.sin(aberration_angle)
    new_y: float = x * np.sin(aberration_angle) + y * np.cos(aberration_angle)

    return (new_x, new_y, z)


def MSO_TO_MSM(data: pd.DataFrame, reverse=False) -> pd.DataFrame:
    """Changes from the MSO to the MSM coordinate system.

    MSO is defined by pointing the x axis towards the Sun, the y
    axis pointing away from Mercury's orbital velocity, and z
    completing the right handed set. The origin is at the centre
    of Mercury.

    MSM is similarly defined, with the origin shifted to be at the
    centre of the dipole field. The x and z axes theoretically
    point along new directions, but the change in angle is
    negligible and ignored.

    This function subtracts 479 km from the z component to convert
    from MSO to MSM. And if reverese, adds 479 km to z.

    Note that this does not change the range. Range always is
    distance to centre of planet.


    Parameters
    ----------
    data : pandas.DataFrame
        Data as a pandas dataframe, typically loaded using `Load_Messenger()`.

    reverse : bool {False}, optional
        If reverse, changes from MSM to MSO.


    Returns
    -------
    data : pandas.DataFrame
        The input data with the ephemeris and frame columns adjusted.
        There is no change to MAG data.
    """
    if not reverse:
        if np.all(data["frame"] == "MSM"):
            print("WARNING: Data is already in MSM frame, no changes were made.")
            return data

        data["eph_z"] = data["eph_z"] - Constants.DIPOLE_OFFSET_RADII

        data["frame"] = "MSM"

    else:
        if np.all(data["frame"] == "MSO"):
            print("WARNING: Data is already in MSO frame, no changes were made.")
            return data

        data["eph_z"] = data["eph_z"] + Constants.DIPOLE_OFFSET_RADII

        data["frame"] = "MSO"

    return data


def MSM_TO_MSO(data: pd.DataFrame) -> pd.DataFrame:
    """See `MSO_TO_MSM()`"""
    return MSO_TO_MSM(data, reverse=True)


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

    x = data["mag_x"]
    y = data["mag_y"]
    z = data["mag_z"]

    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arctan2(y, x) * 180 / np.pi
    phi = np.arctan2(z, r) * 180 / np.pi

    data["mag_r"] = r
    data["mag_theta"] = theta
    data["mag_phi"] = phi

    return data
