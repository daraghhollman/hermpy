import datetime as dt

import matplotlib.pyplot as plt
import spiceypy as spice

from hermpy import mag, plotting_tools

root_dir = "/home/daraghhollman/Main/data/mercury/messenger/mag/avg_1_second/"
metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"

start = dt.datetime(year=2012, month=5, day=11, hour=11)
end = dt.datetime(year=2012, month=5, day=12, hour=12)

# Isolating only a particular portion of the files
data = mag.Load_Between_Dates(
    "/home/daraghhollman/Main/data/mercury/messenger/mag/avg_1_second/", start, end
)

print(data)

"""
This data object is a Pandas DataFrame, and has the following columns:

date:  a datetime object of the time of the measurement
frame: the current coordinate system
eph_x: the x coordinate of the spacecraft (km)
eph_y: the y coordinate of the spacecraft (km)
eph_z: the z coordinate of the spacecraft (km)
range: the distance of the spacecraft from Mercury (km)
mag_x: the magnetic field strength in x (nt)
mag_y: the magnetic field strength in y (nt)
mag_z: the magnetic field strength in z (nt)
mag_total: the total magnetic field strength (nt)
"""

# This data can then be plotted using external libraries
fig, ax = plt.subplots()

ax.plot(data["date"], data["mag_total"])

ax.set_yscale("log")
ax.set_ylabel("|B|")

# Plotting ephemeris information
# We need a metakernel to retrieve ephemeris information
metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"
spice.furnsh(metakernel)
plotting_tools.Add_Tick_Ephemeris(ax)

plt.show()
