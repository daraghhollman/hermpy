import matplotlib.pyplot as plt
from numpy import shape

from MercuryTools import trajectory, plotting_tools

# A metakernel created using AutoMeta
metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"

# we are going to get positions between these two dates
dates = ["2012-06-10", "2012-06-20"]

# Get positions in MSO coordinate system
positions = trajectory.Get_Trajectory("Messenger", dates, metakernel)

# Convert from km to Mercury radii
positions /= 2439.7

# These positions can then be plotted
fig, ax = plt.subplots()

ax.plot(positions[:, 0], positions[:, 1])

# Adding Mercury to plot

plotting_tools.Plot_Mercury(ax, shaded_hemisphere="left")

ax.set_aspect("equal")

plt.show()
