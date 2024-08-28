import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def main():
    data = Load_Messenger(
        [
            "/home/daraghhollman/Main/data/mercury/messenger/mag/2012/01_JAN/MAGMSOSCIAVG12001_01_V08.TAB"
            #"/home/daraghhollman/Main/data/mercury/messenger/mag/2012/01_JAN/MAGMSOSCIAVG12002_01_V08.TAB",
        ]
    )

    start = dt.datetime(year=2012, month=1, day=1, hour=10)
    end = dt.datetime(year=2012, month=1, day=1, hour=14)
    
    data = StripData(data, start, end)

    plt.plot(data["date"], data["mag_total"])
    plt.plot(data["date"], data["mag_x"])
    plt.plot(data["date"], data["mag_y"])
    plt.plot(data["date"], data["mag_z"])
    plt.show()


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
    year, day of year, x, y, z (ephemeris), x, y, z (data), magnitude
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
        ephemeris = np.array([data[:, 7], data[:, 8], data[:, 9] - 479])

        magnetic_field = np.array([data[:, 10], data[:, 11], data[:, 12]])

        dataframe = pd.DataFrame(
            {
                "date": dates,
                "hour": hours,
                "minute": minutes,
                "second": seconds,
                "msm_x": ephemeris[0],
                "msm_y": ephemeris[1],
                "msm_z": ephemeris[2],
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


if __name__ == "__main__":
    main()
