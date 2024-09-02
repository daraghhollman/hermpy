import datetime as dt
import pickle

import matplotlib.pyplot as plt
import pandas as pd


def Load_Crossings(path: str) -> pd.DataFrame:
    """
    Loads a pandas dataframe from pickle file. Expects the following columns:
    [start, end,
    start_x_msm, end_x_msm,
    start_y_msm, end_y_msm,
    start_z_msm, end_z_msm,
    type]
    """
    with open(path, "rb") as crossings_file:
        crossings_data = pickle.load(crossings_file)

    reformatted_crossings_data = pd.DataFrame({
        "start": crossings_data["start"],
        "end": crossings_data["end"],
        "start_x_msm": crossings_data["start_x_msm"],
        "start_y_msm": crossings_data["start_y_msm"],
        "start_z_msm": crossings_data["start_z_msm"],
        "type": crossings_data["Type"],
    })

    return crossings_data


def Plot_Crossing_Intervals(
    ax: plt.Axes, start: dt.datetime, end: dt.datetime, crossings: pd.DataFrame,
):
    """
    Adds vertical lines to a matplotlib axis marking the start and end of crossing intervals
    """

    for _, row in crossings.iterrows():

        # If crossing interval is in plot
        if (row["start"] > start and row["start"] < end) or (
            row["end"] > start and row["end"] < end
        ):

            ax.axvline(row["start"], color="indianred")
            ax.axvline(row["end"], color="cornflowerblue")
