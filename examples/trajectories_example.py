import matplotlib as mpl
import matplotlib.pyplot as plt

from hermpy import plotting_tools, trajectory

mpl.rcParams["font.size"] = 14

# A metakernel created using AutoMeta
metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"

# we are going to get positions between these two dates
dates = ["2012-06-10", "2012-06-12"]

frame = "MSM"

# Get positions in MSO coordinate system
positions = trajectory.Get_Trajectory("Messenger", dates, metakernel, frame=frame)

# Convert from km to Mercury radii
positions /= 2439.7

# These positions can then be plotted
fig, axes = plt.subplots(1, 3)

axes[0].plot(positions[:, 0], positions[:, 1])
axes[1].plot(positions[:, 0], positions[:, 2])
axes[2].plot(positions[:, 1], positions[:, 2])


planes = ["xy", "xz", "yz"]
for i, ax in enumerate(axes):
    plotting_tools.Plot_Mercury(axes[i], shaded_hemisphere="left", plane=planes[i], frame=frame)
    plotting_tools.AddLabels(axes[i], planes[i], frame=frame)
    plotting_tools.PlotMagnetosphericBoundaries(ax, plane=planes[i])
    plotting_tools.SquareAxes(ax, 6)

fig.suptitle("MESSENGER Trajectory 2012-06-10 to 2012-06-12")
plt.show()
