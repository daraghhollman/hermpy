"""
Script to take an input crossing from a crossing list, plot the surrouding trajectory as well as the point, and compare to a calculation of the grazing angle.
"""

import datetime as dt

from hermpy.utils import User, Constants
import hermpy.boundaries as boundaries
import hermpy.trajectory as traj
import hermpy.plotting as hermplot
import hermpy.mag as mag

import matplotlib.pyplot as plt
import numpy as np

# Choose index at which to sample the crossing list
crossings = boundaries.Load_Crossings(
    User.CROSSING_LISTS["Philpott"], include_data_gaps=False
)
crossings = crossings.loc[crossings["Type"].str.contains("BS")]

for _, crossing in crossings.iterrows():
    # Get middle time of the crossing
    crossing_middle_time = (
        crossing["Start Time"] + (crossing["End Time"] - crossing["Start Time"]) / 2
    )

    crossing_position = (
        traj.Get_Position(
            "MESSENGER",
            crossing_middle_time,
            frame="MSM",
            aberrate=True,
        )
        / Constants.MERCURY_RADIUS_KM
    )

    # Determine which boundary function to use, based on crossing type
    if "BS" in crossing["Type"]:
        boundary_function = "bow shock"

    elif "MP" in crossing["Type"]:
        boundary_function = "magnetopause"

    else:
        raise ValueError(
            f"No boundary function matching crossing type: {crossing['Type']}"
        )

    # Compute the grazing angle for this crossing
    grazing_angle, boundary_normal, velocity = traj.Get_Grazing_Angle(
        crossing, function=boundary_function, return_vectors=True
    )

    # Get trajectory for some time susrounding the crossing
    crossing_time_buffer = dt.timedelta(hours=6)

    # Load trajectory
    data = mag.Load_Between_Dates(
        User.DATA_DIRECTORIES["MAG"],
        crossing["Start Time"] - crossing_time_buffer,
        crossing["End Time"] + crossing_time_buffer,
        strip=True,
        aberrate=True,
    )

    # 1 panel plot
    fig, ax = plt.subplots()

    ax.plot(
        data["X MSM' (radii)"],
        np.sqrt(data["Y MSM' (radii)"] ** 2 + data["Z MSM' (radii)"] ** 2),
        c="green",
    )

    ax.scatter(
        crossing_position[0],
        np.sqrt(crossing_position[1] ** 2 + crossing_position[2] ** 2),
        c="purple",
        zorder=10,
    )

    vector_length = 1
    ax.arrow(
        crossing_position[0],
        np.sqrt(crossing_position[1] ** 2 + crossing_position[2] ** 2),
        vector_length * boundary_normal[0],
        vector_length * boundary_normal[1],
        width=0.01,
        head_width=0.1,
        head_length=0.1,
        ec="black",
        fc="black",
        zorder=5,
    )
    ax.arrow(
        crossing_position[0],
        np.sqrt(crossing_position[1] ** 2 + crossing_position[2] ** 2),
        vector_length * velocity[0],
        vector_length * velocity[1],
        width=0.01,
        head_width=0.1,
        head_length=0.1,
        ec="black",
        fc="black",
        zorder=5,
    )

    ax.set_xlim(-2, 2)
    ax.set_ylim(0, 3.6)
    hermplot.Plot_Magnetospheric_Boundaries(ax)
    hermplot.Format_Cylindrical_Plot(ax)

    ax.annotate(
        f"Crossing: {crossing['Type']}\nStarting: {crossing['Start Time']}\nGrazing Angle: {grazing_angle:.2f}$^\circ$",
        xy=(1, 1),
        xycoords="axes fraction",
        size=10,
        ha="right",
        va="top",
        bbox=dict(boxstyle="round", fc="w"),
    )

    plt.show()
