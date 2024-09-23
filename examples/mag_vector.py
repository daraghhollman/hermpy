"""
Script to determine and plot the magnetic field vector as 
polar spherical coordinates.

We define theta as the angle in the xy plane, and phi as the
angle in the perpendicular plane.
"""

import datetime as dt

import matplotlib.pyplot as plt

import hermpy.mag as mag
import hermpy.boundary_crossings as boundaries
import hermpy.plotting_tools as hermplot

# Define some paths we'll need later
root_dir = "/home/daraghhollman/Main/data/mercury/messenger/mag/avg_1_second/"
metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"
philpott_crossings = boundaries.Load_Crossings("/home/daraghhollman/Main/mercury/philpott_crossings.p")

data = mag.Load_Messenger(
    [
        root_dir + "2012/01_JAN/MAGMSOSCIAVG12001_01_V08.TAB",
    ]
)

start = dt.datetime(year=2012, month=1, day=1, hour=6, minute=50)
end = dt.datetime(year=2012, month=1, day=1, hour=12, minute=10)

# Isolating only a particular portion of the files
data = mag.StripData(data, start, end)

# Converting to MSM
data = mag.MSO_TO_MSM(data)

# Accounting for solar wind aberration angle
data = mag.AdjustForAberration(data)

# Converting to polars
data = mag.Convert_To_Polars(data)


fig, axes = plt.subplots(3, 1, sharex=True)

ax1, ax2, ax3 = axes

# Plotting Data
ax1.plot(data["date"], data["mag_r"], color="black", lw=0.8)
ax2.plot(data["date"], data["mag_theta"], color="black", lw=0.8)
ax3.plot(data["date"], data["mag_phi"], color="black", lw=0.8)

ax1.set_ylabel("R")
ax2.set_ylabel(r"$\theta$")
ax3.set_ylabel(r"$\phi$")

ax2.set_ylim(-180, 180)
ax3.set_ylim(-180, 180)

for ax in axes:
    # Adding boundaries
    boundaries.Plot_Crossing_Intervals(ax, start, end, philpott_crossings)


# Add ephemeries ticks
hermplot.Add_Tick_Ephemeris(ax3, metakernel)


plt.show()
