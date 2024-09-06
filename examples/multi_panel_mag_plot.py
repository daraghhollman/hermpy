import datetime as dt

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from hermean_toolbelt import mag, plotting_tools

mpl.rcParams["font.size"] = 14

root_dir = "/home/daraghhollman/Main/data/mercury/messenger/mag/"

data = mag.Load_Messenger(
    [
        root_dir + "2011/04_APR/MAGMSOSCIAVG11101_01_V08.TAB",
    ]
)

start = dt.datetime(year=2011, month=4, day=11, hour=5, minute=0)
end = dt.datetime(year=2011, month=4, day=11, hour=5, minute=30)

# Isolating only a particular portion of the files
data = mag.StripData(data, start, end)

# Converting to MSM
data = mag.MSO_TO_MSM(data)

# Accounting for solar wind aberration angle
data = mag.AdjustForAberration(data)

# This data can then be plotted using external libraries
fig, axes = plt.subplots(4, 1, sharex=True)

to_plot = ["mag_x", "mag_y", "mag_z", "mag_total"]
y_labels = ["B$_x$", "B$_y$", "B$_z$", "|B|"]

ax: plt.Axes
for i, ax in enumerate(axes):

    # Plot Data
    ax.plot(data["date"], data[to_plot[i]], color="black", lw=0.8)
    ax.set_ylabel(y_labels[i])

    # Plot hline at 0
    ax.axhline(0, color="grey", ls="dotted")

    ax.set_xmargin(0)
    ax.tick_params("x", which="major", direction="inout", length=16, width=1)
    ax.tick_params("x", which="minor", direction="inout", length=8, width=0.8)

    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(10))


# Plotting ephemeris information to the last panel
# We need a metakernel to retrieve ephemeris information
metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"
plotting_tools.Add_Tick_Ephemeris(axes[-1], metakernel, include={
    "date", "hours", "minutes", "range", "latitude", "local time" 
})

plt.show()
