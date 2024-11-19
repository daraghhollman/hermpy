import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import pandas as pd


def Reformat_Philpott(input_path: str, output_path: str):
    """Takes Philpott list from suplimetary information and reformat and saves it to csv


    Parameters
    ----------
    input_path : str
        Path to Philpott+ (2020) table S1

    output_path : str
        Path to save the resulting csv


    Returns
    -------
    None
    """

    philpott_csv = pd.read_csv(input_path)

    types = []
    start_times = []
    end_times = []
    start_x = [] # MSO
    start_y = []
    start_z = []
    end_x = []
    end_y = []
    end_z = []

    for i, row in philpott_csv.iterrows():

        # We loop through each row, if the row type is equal to
        # an odd number, it is the start edge of the interval. The
        # following type will be even, and the end edge of the
        # interval.

        if row["Boundary number"] % 2 != 0 or row["Boundary number"] == 10:

            match row["Boundary number"]:
                case 1:
                    types.append("BS_IN")

                case 3:
                    types.append("MP_IN")

                case 5:
                    types.append("MP_OUT")

                case 7:
                    types.append("BS_OUT")

                # 9 and 10 represent data gaps
                case 9:
                    continue

                case 10:
                    continue

                case _:
                    print(row["Boundary number"])

            start_string = f"{row['Year']}{row['Day of year']}{row['Hour']}{row['Minute']}{row['Second']}"
            start_time = dt.datetime.strptime(start_string, "%Y.0%j.0%H.0%M.0%S.%f")
            start_times.append(start_time)

            start_x.append(row["X_MSO (km)"])
            start_y.append(row["Y_MSO (km)"])
            start_z.append(row["Z_MSO (km)"])

            next_row = philpott_csv.iloc[i + 1]

            end_string = f"{next_row['Year']}{next_row['Day of year']}{next_row['Hour']}{next_row['Minute']}{next_row['Second']}"
            end_time = dt.datetime.strptime(end_string, "%Y.0%j.0%H.0%M.0%S.%f")
            end_times.append(end_time)

            end_x.append(next_row["X_MSO (km)"])
            end_y.append(next_row["Y_MSO (km)"])
            end_z.append(next_row["Z_MSO (km)"])

    
    # Format this as a dictionary
    list_data = {
        "start": start_times,
        "end": end_times,
        "start_x": start_x,
        "start_y": start_y,
        "start_z": start_z,
        "end_x": end_x,
        "end_y": end_y,
        "end_z": end_z,
        "type": types,
    }

    for column in list_data.keys():
        print(f"{column}: {len(list_data[column])}")

    # Create a pandas dataframe with this information
    pd.DataFrame(list_data).to_csv(output_path)
    



def Load_Crossings(path: str) -> pd.DataFrame:
    """Loads a pandas DataFrame from reformatted csv file

    Parameters
    ----------
    path : str
        An abosolute path to a crossing intervals file.
        Expects the following columns to be present in the
        csv file:
            [start,
             end,
             start_x, end_x,
             start_y, end_y,
             start_z, end_z,
             type
            ]


    Returns
    -------
    Crossings Data : pandas.DataFrame
        A DataFrame of boundary crossing intervals with columns:
            [start,
             end,
             start_x, end_x,
             start_y, end_y,
             start_z, end_z,
             type
            ]
    """
    date_parse_no_ms = lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    date_parse_ms = lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')

    crossings_data = pd.read_csv(path, parse_dates=["start", "end"])
    crossings_data["start"] = pd.to_datetime(crossings_data["start"], format="mixed")
    crossings_data["end"] = pd.to_datetime(crossings_data["end"], format="mixed")

    return crossings_data


def Plot_Crossing_Intervals(
    ax: plt.Axes,
    start: dt.datetime,
    end: dt.datetime,
    crossings: pd.DataFrame,
    label: bool = True,
    height: float = 0.9,
    color: str = "orange",
    lw: float = 1,
) -> None:
    """Adds vertical lines marking the start and end of given
    crossing intervals.

    Detects crossing intervals present in range of data.
    Vertical lines in the form of pyplot.axvlines() are added
    to a pyplot.Axes object `ax`, with optional labelling of
    type.

    Parameters
    ---------
    ax : pyplot.Axes
        The pyplot axis to add the vertical lines to.

    start : datetime.datetime
        The starting point of the data plotted.

    end : datetime.datetime
        The ending point of the data plotted.

    crossings : pandas.DataFrame
        A pandas DataFrame with crossings data, as generated by
        Load_Crossings().

    label : bool {`True`, `False`}
        If `True`, adds a label specificing the boundary type.

    color : str {`orange`, any other matplotlib named colour}


    Returns
    -------
    None
    """

    for _, row in crossings.iterrows():

        # If crossing interval is in plot
        if (row["start"] > start and row["start"] < end) or (
            row["end"] > start and row["end"] < end
        ):
            midpoint = row["start"] + (row["end"] - row["start"]) / 2

            if label:
                ax.text(
                    midpoint,
                    height,
                    row["type"].upper().replace("_", " "),
                    transform=ax.get_xaxis_transform(),
                    color=color,
                    ha="center",
                    va="center",
                )

            ax.axvline(row["start"], color=color, ls="dashed", lw=lw)
            ax.axvline(row["end"], color=color, ls="dashed", lw=lw)


def Plot_Crossings_As_Minutes_Before(
    ax: plt.Axes,
    crossings: pd.DataFrame,
    data_start: dt.datetime,
    data_end: dt.datetime,
    apoapsis_time: dt.datetime,
    label: bool = True,
    height: float = 0.9,
    color: str = "orange",
    show_partial_crossings=True,
) -> None:
    """
    Plots crossings as vlines with respect to the closest
    apoapsis.

    Detects crossing intervals present in range of data.
    Vertical lines in the form of pyplot.axvlines() are added
    to a pyplot.Axes object `ax`, with optional labelling of
    type. A reference `apoapsis_time` is used to convert to
    minutes before apoapsis instead of a date.

    Parameters
    ---------
    ax : pyplot.Axes
        The pyplot axis to add the vertical lines to.

    crossings : pandas.DataFrame
        A pandas DataFrame with crossings data, as generated by
        Load_Crossings().

    data_start : datetime.datetime
        The starting point of the data plotted.

    data_end : datetime.datetime
        The ending point of the data plotted.

    apoapsis_time : datetime.datetime
        The time of the reference apoapsis.

    label : bool {`True`, `False`}
        If `True`, adds a label specificing the boundary type.

    height : float {`0.9`}, optional
        The height of the label in axis units.

    color : str {`orange`, any other matplotlib named colour}, optional
        The colour of the vertical lines and labels.


    Returns
    -------
    None
    """

    for _, row in crossings.iterrows():

        # Check if crossing interval is in plot
        if (row["start"] > data_start and row["start"] < data_end) or (
            row["end"] > data_start and row["end"] < data_end
        ):

            if not show_partial_crossings:
                if not (row["start"] > data_start and row["start"] < data_end) and (
                        row["end"] > data_start and row["end"] < data_end):
                    continue

            midpoint = row["start"] + (row["end"] - row["start"]) / 2

            # Convert times into minutes before apoapsis
            start_minutes = (apoapsis_time - row["start"]).total_seconds() / 60
            end_minutes = (apoapsis_time - row["end"]).total_seconds() / 60

            if label:
                ax.text(
                    (midpoint - data_start).total_seconds()
                    / (data_end - data_start).total_seconds(),
                    height,
                    row["type"].upper().replace("_", " "),
                    transform=ax.transAxes,
                    color=color,
                    ha="center",
                    va="center",
                )

            ax.axvline(start_minutes, color=color, ls="dashed")
            ax.axvline(end_minutes, color=color, ls="dashed")


def Get_Crossings_As_Points(
    crossings: pd.DataFrame, start: dt.datetime, end: dt.datetime
) -> list[list[float]]:
    """Get boundary crossing positions as data points.

    Takes a crossing list input along with a start and stop datetime
    and outputs the positions of any crossings.


    Parameters
    ----------
    crossings : pandas.DataFrame
        A pandas DataFrame with crossings data, as generated by
        Load_Crossings().

    start : datetime.datetime
        The starting point of the search

    end : datetime.datetime
        The ending point of the search


    Returns
    -------
    positions : list[ list[ float ] ]
        A list of positions where boundaries were crossed in that time.
    """

    positions = []

    for _, row in crossings.iterrows():

        # Check if crossing interval is in plot
        if (row["start"] > start and row["start"] < end) or (
            row["end"] > start and row["end"] < end
        ):

            # Get position of midpoint
            midpoint_x_msm = (row["start_x_msm"] + row["end_x_msm"]) / 2
            midpoint_y_msm = (row["start_y_msm"] + row["end_y_msm"]) / 2
            midpoint_z_msm = (row["start_z_msm"] + row["end_z_msm"]) / 2
            position = [midpoint_x_msm, midpoint_y_msm, midpoint_z_msm]

            positions.append(position)

    return positions
