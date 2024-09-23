import datetime as dt

import ephem
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm


def StripData(data: pd.DataFrame, start: dt.datetime, end: dt.datetime) -> pd.DataFrame:
    """
    Removes the start and end of a dataframe (containing a dt.datetime "date" row) to match give start and end time
    """

    stripped_data = data.loc[data["date"].between(start, end)]
    stripped_data = stripped_data.reset_index(drop=True)

    return stripped_data


def Load_Messenger(file_paths: list[str], averaged_measurements=True) -> pd.DataFrame:
    """
    Reads data from a list of file paths and converts to a pandas dataframe in the following format:
    year, day of year, x, y, z (ephemeris mso), x, y, z (data mso), magnitude
    """

    multi_file_data = []
    # Load and concatonate into one dataframe
    for path in file_paths:
        # Read file
        data = np.genfromtxt(path)

        years = data[:, 0]
        day_of_years = data[:, 1]
        hours = data[:, 2]
        minutes = data[:, 3]
        seconds = data[:, 4]

        # Create a list of datetime objects for a new date column
        dates = [dt.datetime(1, 1, 1)] * len(day_of_years)
        for i, day in enumerate(day_of_years):
            date = dt.datetime(
                year=int(years[i]),
                month=1,
                day=1,
                hour=int(hours[i]),
                minute=int(minutes[i]),
                second=int(seconds[i]),
            )
            date += dt.timedelta(days=day - 1)

            dates[i] = date

        # Offset the z of the coordinates due to an asymmetric dipole
        # i.e. convert from MSO to MSM

        if averaged_measurements:
            ephemeris = np.array([data[:, 7], data[:, 8], data[:, 9]])
            magnetic_field = np.array([data[:, 10], data[:, 11], data[:, 12]])

        else:
            ephemeris = np.array([data[:, 6], data[:, 7], data[:, 8]])
            magnetic_field = np.array([data[:, 9], data[:, 10], data[:, 11]])

        dataframe = pd.DataFrame(
            {
                "date": dates,
                "hour": hours,
                "minute": minutes,
                "second": seconds,
                "frame": "MSO",
                "eph_x": ephemeris[0],
                "eph_y": ephemeris[1],
                "eph_z": ephemeris[2],
                "range": np.sqrt(
                    ephemeris[0] ** 2 + ephemeris[1] ** 2 + ephemeris[2] ** 2
                ),
                "mag_x": magnetic_field[0],
                "mag_y": magnetic_field[1],
                "mag_z": magnetic_field[2],
                "mag_total": np.sqrt(
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


def AdjustForAberration(data: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    """
    Solar wind impacts mercury's magnetosphere at an angle from the vector to the sun due to its orbital velocity
    """
    if verbose:
        print("Adjusting for Aberration")

    new_eph_x = []
    new_eph_y = []

    new_mag_x = []
    new_mag_y = []

    r = 0
    aberration_angle = 0
    previous_date = dt.datetime(2010, 1, 1)
    for _, row in tqdm(data.iterrows(), total=len(data), disable=not verbose):

        # check if day has changed and then update mercury distance
        if (row["date"] - previous_date) > dt.timedelta(days=1):
            r = GetDistanceFromSun(row["date"])
            previous_date = row["date"]

            # determine mercury velocity
            a = 57909050 * 1000
            M = 1.9891e30
            G = 6.6743e-11

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


def GetDistanceFromSun(date: dt.datetime) -> float:
    """
    Uses the ephem package to find distance from mercury to the sun
    """
    mercury_ephem = ephem.Mercury()

    # why do we use and epoch of 1970??
    mercury_ephem.compute(date, epoch="1970")

    distance_au = mercury_ephem.sun_distance
    distance_km = distance_au * 1.496e11

    return distance_km


def MSO_TO_MSM(data: pd.DataFrame, reverse=False) -> pd.DataFrame:
    """
    Subtracts from the z component to convert from MSO to MSM.
    Note that angle changes are negligable.
    Reverse option converts from MSM to MSO

    Note that this does not change the range. Range always is distance to centre of planet.
    """
    if not reverse:
        data["eph_z"] = data["eph_z"] - 479

        data["frame"] = "MSM"

    else:
        data["eph_z"] = data["eph_z"] + 479

        data["frame"] = "MSO"

    return data


def MSM_TO_MSO(data: pd.DataFrame) -> pd.DataFrame:
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
