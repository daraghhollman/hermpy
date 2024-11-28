"""
Script to take an input crossing from a crossing list, plot the surrouding trajectory as well as the point, and compare to a calculation of the grazing angle.
"""

import datetime as dt

from hermpy.utils import User, Constants
import hermpy.boundary_crossings as boundaries
import hermpy.trajectory as traj
import hermpy.plotting_tools as hermplot
import hermpy.mag as mag

import matplotlib.pyplot as plt
import numpy as np

# Choose index at which to sample the crossing list
crossing_index = 1585

crossings = boundaries.Load_Crossings(User.CROSSING_LISTS["Philpott"], include_data_gaps=False)
crossing = crossings.iloc[crossing_index]

print(crossing["Start Time"])


"""
# Determine which boundary function to use, based on crossing type
if "BS" in crossing["Type"]:
    boundary_function = "bow shock"

elif "MP" in crossing["Type"]:
    boundary_function = "magnetopause"

else:
    raise ValueError(f"No boundary function matching crossing type: {crossing['Type']}")

# Compute the grazing angle for this crossing
grazing_angle = traj.Get_Grazing_Angle(crossing, function=boundary_function)
"""


# Get trajectory for some time susrounding the crossing
crossing_time_buffer = dt.timedelta(hours=6)

# Load trajectory
data = mag.Load_Between_Dates(User.DATA_DIRECTORIES["MAG"],
                               crossing["Start Time"] - crossing_time_buffer,
                               crossing["End Time"] + crossing_time_buffer,
                               strip=True,
                               aberrate=True,
)

positions = traj.Get_Trajectory("MESSENGER",
                               [crossing["Start Time"] - crossing_time_buffer,
                                crossing["End Time"] + crossing_time_buffer],
                                steps=200,
                                frame="MSM",
                                aberrate=True,
) / Constants.MERCURY_RADIUS_KM

# 1 panel plot
fig, ax = plt.subplots()

ax.plot(data["X MSM' (radii)"], np.sqrt(data["Y MSM' (radii)"] ** 2 + data["Z MSM' (radii)"] ** 2), c="green")
ax.plot(positions[:,0], np.sqrt(positions[:,1] ** 2 + positions[:,2] ** 2), c="k")

ax.set_xlim(-2, 2)
ax.set_ylim(0, 3.6)
hermplot.Plot_Magnetospheric_Boundaries(ax)
# hermplot.Plot_Mercury(ax, shaded_hemisphere="left")

plt.show()


# 2 panel plot
fig, (xy_axis, xz_axis) = plt.subplots(1, 2)

xy_axis.plot(data["X MSM' (radii)"], data["Y MSM' (radii)"], c="green")
xy_axis.plot(positions[:,0], positions[:,1], c="k")

xz_axis.plot(data["X MSM' (radii)"], data["Z MSM' (radii)"], c="green")
xz_axis.plot(positions[:,0], positions[:,2], c="k")

hermplot.Plot_Mercury(ax, shaded_hemisphere="left")

plt.show()
