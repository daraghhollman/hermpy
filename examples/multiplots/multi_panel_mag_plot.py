import datetime as dt

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import spiceypy as spice

from hermpy import mag, plotting_tools

mpl.rcParams["font.size"] = 14

root_dir = "/home/daraghhollman/Main/data/mercury/messenger/mag/avg_1_second/"
metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"
spice.furnsh(metakernel)

start = dt.datetime(year=2011, month=4, day=11, hour=5, minute=0)
end = dt.datetime(year=2011, month=4, day=11, hour=5, minute=30)

data = mag.Load_Between_Dates(root_dir, start, end, strip=True, aberrate=True)

# This data can then be plotted using external libraries
fig, axes = plt.subplots(4, 1, sharex=True)

to_plot = ["Bx", "By", "Bz", "|B|"]
y_labels = ["B$_x$", "B$_y$", "B$_z$", "|B|"]

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
plotting_tools.Add_Tick_Ephemeris(axes[-1])
plt.show()
