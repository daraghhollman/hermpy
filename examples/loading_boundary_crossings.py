import datetime as dt

import matplotlib.pyplot as plt

from MercuryTools import boundary_crossings, mag

sun_crossings = boundary_crossings.Load_Crossings("../../sun_crossings.p")

philpott_crossings = boundary_crossings.Load_Crossings("../../philpott_crossings.p")


### This section as shown in mag_example.py
root_dir = "/home/daraghhollman/Main/data/mercury/messenger/mag/"
# Loading data, downloaded from PDS
data = mag.Load_Messenger(
    [
        root_dir + "2012/01_JAN/MAGMSOSCIAVG12001_01_V08.TAB",
    ]
)

# Isolating only a particular portion of the files
start = dt.datetime(year=2012, month=1, day=1, hour=9)
end = dt.datetime(year=2012, month=1, day=1, hour=15)
data = mag.StripData(data, start, end)

fig, ax = plt.subplots()

ax.plot(data["date"], data["mag_total"], color="black")
### ---------------------------------------

ax.set_ylabel("|B| [nT]")
ax.set_xlabel("UTC")
ax.set_yscale("log")

# Plotting crossing intervals as axvlines
boundary_crossings.Plot_Crossing_Intervals(ax, start, end, philpott_crossings)

plt.show()
