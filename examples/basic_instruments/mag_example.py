import datetime as dt

import matplotlib.pyplot as plt

from hermpy import mag, plotting_tools, boundary_crossings

root_dir = "/home/daraghhollman/Main/data/mercury/messenger/mag/avg_1_second/"

start = dt.datetime(year=2011, month=10, day=15, hour=14, minute=15, second=0)
end = dt.datetime(year=2011, month=10, day=15, hour=15, minute=0, second=0)

# Isolating only a particular portion of the files
data = mag.Load_Between_Dates(
    "/home/daraghhollman/Main/data/mercury/messenger/mag/avg_1_second/", start, end, strip=True, aberrate=True
)

# This data can then be plotted using external libraries
fig, ax = plt.subplots()

ax.plot(data["date"], data["|B|"])

ax.set_yscale("log")
ax.set_ylabel("|B|")

# Plotting ephemeris information
# We need a metakernel to retrieve ephemeris information
plotting_tools.Add_Tick_Ephemeris(ax)

plt.show()
