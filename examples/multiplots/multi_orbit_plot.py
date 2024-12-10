import datetime as dt
from glob import glob

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import spiceypy as spice

from hermpy import boundaries, mag, plotting, trajectory, utils

mpl.rcParams["font.size"] = 18

############################################################
#################### LOADING FILES #########################
############################################################

root_dir = "/home/daraghhollman/Main/data/mercury/messenger/mag/avg_1_second/"

metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"
spice.furnsh(metakernel)

philpott_crossings = boundaries.Load_Crossings(
    "/home/daraghhollman/Main/Work/mercury/DataSets/philpott_2020.xlsx"
)

# Define the time segement we want to look at
# Specifically, the time segmenet of the centre orbit.
# We can convert this to minutes before / after apoapsis
# to look at the same time in other orbits
start = dt.datetime(year=2011, month=3, day=31, hour=3, minute=20)
end = dt.datetime(year=2011, month=3, day=31, hour=4, minute=5)
data_length = end - start

# Determine the file padding needed to display all the orbits wanted
search_start = start - dt.timedelta(days=2)
search_end = end + dt.timedelta(days=2)

data = mag.Load_Between_Dates(
    root_dir, search_start, search_end, strip=True, aberrate=True
)

#############################################################
##################### FINDING ORBITS ########################
#############################################################

# Set the number of orbits either side
number_of_orbits = 5
approx_orbit_period = dt.timedelta(hours=12)

apoapsis_altitudes, apoapsis_times = trajectory.Get_All_Apoapsis_In_Range(
    start - number_of_orbits * approx_orbit_period,
    start + number_of_orbits * approx_orbit_period,
    number_of_orbits_to_include=5,
)

# Determine how far before apoapsis our start time is.
middle_index = len(apoapsis_times) // 2

middle_apoapsis_time = apoapsis_times[middle_index]
middle_apoapsis_altitude = apoapsis_altitudes[middle_index]


middle_data = mag.Strip_Data(data, start, end)

# Create new column in data for minutes before apoapsis
minutes_before_apoapsis = []

for date in middle_data["date"]:
    minutes_before_apoapsis.append((middle_apoapsis_time - date).total_seconds() / 60)

middle_data["minutes before apoapsis"] = minutes_before_apoapsis

minutes_before = middle_data["minutes before apoapsis"][0]


data_groups = []
for apoapsis_time in apoapsis_times:

    start_time = apoapsis_time - dt.timedelta(minutes=minutes_before)
    end_time = start_time + data_length

    new_data = mag.Strip_Data(
        data,
        start_time,
        end_time,
    )

    new_data["minutes before apoapsis"] = minutes_before_apoapsis

    data_groups.append(new_data)

####################################################
################## PLOTTING MAG ####################
####################################################

fig = plt.figure()

ax1 = plt.subplot2grid((2 + len(data_groups), 3), (0, 0), colspan=1, rowspan=2)
ax2 = plt.subplot2grid((2 + len(data_groups), 3), (0, 1), colspan=1, rowspan=2)
ax3 = plt.subplot2grid((2 + len(data_groups), 3), (0, 2), colspan=1, rowspan=2)
trajectory_axes = [ax1, ax2, ax3]


mag_axes: list = [0] * len(data_groups)

for i in range(len(data_groups)):
    mag_axes[i] = plt.subplot2grid((2 + len(data_groups), 3), (i + 2, 0), colspan=3)

mag_axes[0].set_title(" ")

for i, orbit_data in enumerate(data_groups):

    ax = mag_axes[i]

    if i == middle_index:
        colour = "magenta"
        label = f"{orbit_data['date'].iloc[0].strftime("%Y-%m-%d %H:%M:%S")} to\n{orbit_data['date'].iloc[-1].strftime("%Y-%m-%d %H:%M:%S")}"

    else:
        colour = "black"

        if (i - middle_index) < 0:
            label = f"{abs(i - middle_index)} orbit(s) before"
        else:
            label = f"{i - middle_index} orbit(s) after"

        ax.plot(
            data_groups[middle_index]["minutes before apoapsis"],
            data_groups[middle_index]["|B|"],
            color="magenta",
            lw=0.8,
            alpha=0.5,
        )

    ax.plot(
        orbit_data["minutes before apoapsis"],
        orbit_data["|B|"],
        color=colour,
        lw=0.8,
    )

    ax.text(
        1.05,
        0.5,
        label,
        rotation=-90,
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=14,
        transform=ax.transAxes,
    )

    boundaries.Plot_Crossings_As_Minutes_Before(
        ax,
        philpott_crossings,
        orbit_data["date"].iloc[0],
        orbit_data["date"].iloc[-1],
        apoapsis_times[i],
    )

    ax.set_xlim(minutes_before, np.min(orbit_data["minutes before apoapsis"]))

    ax.set_xmargin(0)
    ax.tick_params("x", which="major", direction="inout", length=16, width=1)
    ax.tick_params("x", which="minor", direction="inout", length=8, width=0.8)

    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(10))

    if ax != mag_axes[-1]:
        ax.set_xticklabels([])

mag_axes[-1].set_xlabel("Minutes before apoapsis")
mag_axes[middle_index].set_ylabel("|B| [nT]")
# fig.text(0.06, 0.35, "|B| [nT]", ha="center", va="center", rotation="vertical")


#################################################################
################### PLOTING TRAJECTORIES ########################
#################################################################

# Here we just plot the trajectory of the middle orbit, along with some padding

frame = "MSM"


time_padding = dt.timedelta(hours=6)

start = data_groups[middle_index]["date"].iloc[0]
end = data_groups[middle_index]["date"].iloc[-1]

dates = [start, end]

padded_dates = [
    (start - time_padding),
    (end + time_padding),
]

positions = trajectory.Get_Trajectory("Messenger", dates, frame=frame, aberrate=True)
padded_positions = trajectory.Get_Trajectory(
    "Messenger", padded_dates, frame=frame, aberrate=True
)

# Convert from km to Mercury radii
positions /= utils.Constants.MERCURY_RADIUS_KM
padded_positions /= utils.Constants.MERCURY_RADIUS_KM


trajectory_axes[0].plot(
    positions[:, 0], positions[:, 1], color="magenta", lw=3, zorder=10
)
trajectory_axes[1].plot(
    positions[:, 0],
    positions[:, 2],
    color="magenta",
    lw=3,
    zorder=10,
    label="Plotted Trajectory",
)
trajectory_axes[2].plot(
    positions[:, 1], positions[:, 2], color="magenta", lw=3, zorder=10
)
trajectory_axes[0].plot(padded_positions[:, 0], padded_positions[:, 1], color="grey")
trajectory_axes[1].plot(
    padded_positions[:, 0],
    padded_positions[:, 2],
    color="grey",
    label=r"Trajectory $\pm$ "
    + str(int(time_padding.total_seconds() / 3600))
    + " hours",
)
trajectory_axes[2].plot(padded_positions[:, 1], padded_positions[:, 2], color="grey")

planes = ["xy", "xz", "yz"]
shaded = ["left", "left", "none"]
for i, ax in enumerate(trajectory_axes):
    plotting.Plot_Mercury(
        ax, shaded_hemisphere=shaded[i], plane=planes[i], frame=frame
    )
    plotting.Add_Labels(ax, planes[i], frame=frame)
    plotting.Plot_Magnetospheric_Boundaries(ax, plane=planes[i], add_legend=True)
    plotting.Square_Axes(ax, 4)

trajectory_axes[1].legend(
    bbox_to_anchor=(0.5, 1.2), loc="center", ncol=2, borderaxespad=0.5
)

plt.show()
