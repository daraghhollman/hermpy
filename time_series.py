import datetime as dt

import ephem
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm


def main():

    pd.set_option('display.max_columns', 20)
    data = Load_Messenger(
        [
            "/home/daraghhollman/Main/data/mercury/messenger/mag/2014/01_JAN/MAGMSOSCIAVG14001_01_V08.TAB"
            #"/home/daraghhollman/Main/data/mercury/messenger/mag/2012/01_JAN/MAGMSOSCIAVG12001_01_V08.TAB"
            # "/home/daraghhollman/Main/data/mercury/messenger/mag/2012/01_JAN/MAGMSOSCIAVG12002_01_V08.TAB",
        ]
    )

    start = dt.datetime(year=2014, month=1, day=1, hour=0, minute=0, second=1)
    end = dt.datetime(year=2014, month=1, day=1, hour=0, minute=1, second=20)

    data = StripData(data, start, end)
    data = MSO_TO_MSM(data)

    data = AdjustForAberration(data)

    print(data)

    #plt.plot(data["date"], data["mag_total"], color="black", label="|B|")
    #plt.plot(data["date"], data["mag_x"], color="indianred", label=r"B$_x$")
    #plt.plot(data["date"], data["mag_y"], color="cornflowerblue", label=r"B$_y$")
    #plt.plot(data["date"], data["mag_z"], color="turquoise", label=r"B$_z$")

    #plt.legend()
    #plt.show()


def StripData(data: pd.DataFrame, start: dt.datetime, end: dt.datetime):
    """
    Removes the start and end of a dataframe (containing a dt.datetime "date" row) to match give start and end time
    """

    indices_to_keep = data.index[(data["date"] >= start) & (data["date"] <= end)]
    stripped_data = data[data.index.isin(indices_to_keep)]

    return stripped_data


def Load_Messenger(file_paths: list):
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
        ephemeris = np.array([data[:, 7], data[:, 8], data[:, 9]])

        magnetic_field = np.array([data[:, 10], data[:, 11], data[:, 12]])

        dataframe = pd.DataFrame(
            {
                "date": dates,
                "hour": hours,
                "minute": minutes,
                "second": seconds,
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

    return multi_file_data


def AdjustForAberration(data: pd.DataFrame):
    """
    Solar wind impacts mercury's magnetosphere at an angle from the vector to the sun due to its orbital velocity
    """
    print("Adjusting for Aberration")

    new_eph_x = []
    new_eph_y = []

    new_mag_x = []
    new_mag_y = []

    r = 0
    aberration_angle = 0
    previous_date = dt.datetime(2010, 1, 1)
    for _, row in tqdm(data.iterrows(), total=len(data)):

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
        new_mag = (row["mag_x"] * np.cos(aberration_angle) - row["mag_y"] * np.sin(aberration_angle),
                   row["mag_x"] * np.sin(aberration_angle) + row["mag_y"] * np.cos(aberration_angle))

        new_ephem = (row["eph_x"] * np.cos(aberration_angle) - row["eph_y"] * np.sin(aberration_angle),
                     row["eph_x"] * np.sin(aberration_angle) + row["eph_y"] * np.cos(aberration_angle))

        new_eph_x.append(new_ephem[0])
        new_eph_y.append(new_ephem[1])

        new_mag_x.append(new_mag[0])
        new_mag_y.append(new_mag[1])

    data["eph_x"] = new_eph_x
    data["eph_y"] = new_eph_y
    data["mag_x"] = new_mag_x
    data["mag_y"] = new_mag_y

    return data


def GetDistanceFromSun(date: pd.DataFrame):
    """
    Uses the ephem package to find distance from mercury to the sun
    """
    mercury_ephem = ephem.Mercury()

    # why do we use and epoch of 1970??
    mercury_ephem.compute(date, epoch="1970")

    distance_au = mercury_ephem.sun_distance
    distance_km = distance_au * 1.496e11

    return distance_km


def MSO_TO_MSM(data: pd.DataFrame, reverse=False):
    """
    Subtracts from the z component to convert from MSO to MSM.
    Note that angle changes are negligable.
    Reverse option converts from MSM to MSO

    Note that this does not change the range. Range always is distance to centre of planet.
    """
    if not reverse:
        data["eph_z"] = data["eph_z"] - 479

    else:
        data["eph_z"] = data["eph_z"] + 479

    return data


def MSM_TO_MSO(data):
    return MSO_TO_MSM(data, reverse=True)


if __name__ == "__main__":
    main()
