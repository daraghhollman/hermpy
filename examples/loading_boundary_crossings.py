import datetime as dt

import spiceypy as spice
import matplotlib as mpl
import matplotlib.pyplot as plt

from hermpy import boundary_crossings, mag, plotting_tools

mpl.rcParams["font.size"] = 14


#sun_crossings = boundary_crossings.Load_Crossings("../../sun_crossings.p")
philpott_crossings = boundary_crossings.Load_Crossings("../../philpott_2020_reformatted.csv")


### This section as shown in mag_example.py
root_dir = "/home/daraghhollman/Main/data/mercury/messenger/mag/avg_1_second/"
# Loading data, downloaded from PDS
data = mag.Load_Messenger(
    [
        root_dir + "2014/01_JAN/MAGMSOSCIAVG14017_01_V08.TAB",
    ]
)

# Isolating only a particular portion of the files
start = dt.datetime(year=2014, month=1, day=17, hour=2, minute=0)
end = dt.datetime(year=2014, month=1, day=17, hour=2, minute=40)
data = mag.Strip_Data(data, start, end)

fig, ax = plt.subplots()

ax.plot(data["date"], data["mag_total"], color="black")
### ---------------------------------------

ax.set_ylabel("|B| [nT]")
ax.set_yscale("log")
ax.set_xmargin(0)
ax.tick_params(which="major", direction="out", length=16, width=1.5)
ax.tick_params(which="minor", direction="out", length=8, width=1)

# Plotting crossing intervals as axvlines
boundary_crossings.Plot_Crossing_Intervals(ax, start, end, philpott_crossings)

# Plotting ephemeris information
# We need a metakernel to retrieve ephemeris information
metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"
spice.furnsh(metakernel)
plotting_tools.Add_Tick_Ephemeris(ax, include={
    "date", "hours", "minutes", "range", "latitude", "local time" 
})

plt.show()
