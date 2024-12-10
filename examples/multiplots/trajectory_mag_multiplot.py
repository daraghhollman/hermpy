import datetime as dt

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import spiceypy as spice

from hermpy import mag, plotting, trajectory, boundaries

mpl.rcParams["font.size"] = 14


###################### MAG #########################
root_dir = "/home/daraghhollman/Main/data/mercury/messenger/mag/avg_1_second/"
philpott_crossings = boundaries.Load_Crossings("/home/daraghhollman/Main/Work/mercury/DataSets/philpott_2020.xlsx")

# We need a metakernel to retrieve ephemeris information
metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"

spice.furnsh(metakernel)
start = dt.datetime(year=2011, month=9, day=26, hour=12, minute=23)
end = dt.datetime(year=2011, month=9, day=26, hour=12, minute=59)

data = mag.Load_Between_Dates(root_dir, start, end, strip=True, aberrate=True)

# This data can then be plotted using external libraries
fig = plt.figure()

ax1 = plt.subplot2grid((6, 3), (0, 0), colspan=1, rowspan=2)
ax2 = plt.subplot2grid((6, 3), (0, 1), colspan=1, rowspan=2)
ax3 = plt.subplot2grid((6, 3), (0, 2), colspan=1, rowspan=2)
trajectory_axes = [ax1, ax2, ax3]

ax4 = plt.subplot2grid((6, 3), (2, 0), colspan=3)
ax5 = plt.subplot2grid((6, 3), (3, 0), colspan=3)
ax6 = plt.subplot2grid((6, 3), (4, 0), colspan=3)
ax7 = plt.subplot2grid((6, 3), (5, 0), colspan=3)
mag_axes = [ax4, ax5, ax6, ax7]

ax4.set_title(" ")

to_plot = ["Bx", "By", "Bz", "|B|"]
y_labels = ["B$_x$", "B$_y$", "B$_z$", "|B|"]

for i, ax in enumerate(mag_axes):

    # Plot Data
    ax.plot(data["date"], data[to_plot[i]], color="black", lw=0.8)
    ax.set_ylabel(y_labels[i])

    # Plot hline at 0
    ax.axhline(0, color="grey", ls="dotted")

    ax.set_xmargin(0)
    ax.tick_params("x", which="major", direction="inout", length=16, width=1)
    ax.tick_params("x", which="minor", direction="inout", length=8, width=0.8)

    # Plotting crossing intervals as axvlines
    boundaries.Plot_Crossing_Intervals(ax, start, end, philpott_crossings, label=True)

    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(10))


# Plotting ephemeris information to the last panel
plotting.Add_Tick_Ephemeris(
    mag_axes[-1],
    include={"date", "hours", "minutes", "range", "latitude", "local time"},
)

for ax in mag_axes:
    # For some reason sharex works differently for subplot2grid so we need
    # to remove tick labels manually
    if ax != mag_axes[-1]:
        ax.set_xticklabels([])



##################### TRAJECTORIES ######################
# Add trajectory subplot

# we are going to get positions between these two dates
time_padding = dt.timedelta(hours=6)
dates = [start, end]
padded_dates = [
    (start - time_padding),
    (end + time_padding),
]

frame = "MSM"

# Get positions in MSO coordinate system
positions = trajectory.Get_Trajectory("Messenger", dates, frame=frame, aberrate=True)
padded_positions = trajectory.Get_Trajectory("Messenger", padded_dates, frame=frame, aberrate=True)

# Convert from km to Mercury radii
positions /= 2439.7
padded_positions /= 2439.7

trajectory_axes[0].plot(positions[:, 0], positions[:, 1], color="magenta", lw=3, zorder=10)
trajectory_axes[1].plot(positions[:, 0], positions[:, 2], color="magenta", lw=3, zorder=10, label="Plotted Trajectory")
trajectory_axes[2].plot(positions[:, 1], positions[:, 2], color="magenta", lw=3, zorder=10)

# We also would like to give context and plot the orbit around this
trajectory_axes[0].plot(padded_positions[:, 0], padded_positions[:, 1], color="grey")
trajectory_axes[1].plot(padded_positions[:, 0], padded_positions[:, 2], color="grey", label=r"Trajectory $\pm$ 6 hours")
trajectory_axes[2].plot(padded_positions[:, 1], padded_positions[:, 2], color="grey")

planes = ["xy", "xz", "yz"]
for i, ax in enumerate(trajectory_axes):
    plotting.Plot_Mercury(
        ax, shaded_hemisphere="left", plane=planes[i], frame=frame
    )
    plotting.Add_Labels(ax, planes[i], frame=frame)
    plotting.Plot_Magnetospheric_Boundaries(ax, plane=planes[i], add_legend=True)
    plotting.Square_Axes(ax, 4)

trajectory_axes[1].legend(bbox_to_anchor=(0.5, 1.2), loc="center", ncol=2, borderaxespad=0.5)

plt.show()
