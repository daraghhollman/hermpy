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

# This data can then be plotted using external libraries
fig, ax = plt.subplots()

ax.plot(data["date"], data["|B|"])

ax.set_yscale("log")
ax.set_ylabel("|B|")

# Plotting ephemeris information
# We need a metakernel to retrieve ephemeris information
metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"
spice.furnsh(metakernel)
plotting_tools.Add_Tick_Ephemeris(ax)

plt.show()
