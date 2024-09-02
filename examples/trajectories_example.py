import matplotlib.pyplot as plt
from pandas import plotting

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

# In the xy plane
plotting_tools.Plot_Mercury(ax, shaded_hemisphere="left")
plotting_tools.PlotMagnetosphericBoundaries(ax)

plotting_tools.SquareAxes(ax, 8)
plotting_tools.AddLabels(ax, "xy")

plt.show()
