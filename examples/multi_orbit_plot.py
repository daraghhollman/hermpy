import datetime as dt

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import spiceypy as spice

from hermean_toolbelt import mag, plotting_tools, trajectory

mpl.rcParams["font.size"] = 14

############################################################
#################### LOADING FILES #########################
############################################################

root_dir = "/home/daraghhollman/Main/data/mercury/messenger/mag/"

metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"

data = mag.Load_Messenger(
    [
        root_dir + "2011/04_APR/MAGMSOSCIAVG11100_01_V08.TAB",
        root_dir + "2011/04_APR/MAGMSOSCIAVG11101_01_V08.TAB",
        root_dir + "2011/04_APR/MAGMSOSCIAVG11102_01_V08.TAB",
    ]
)

# Define the time segement we want to look at
# Specifically, the time segmenet of the centre orbit.
# We can convert this to minutes before / after apoapsis
# to look at the same time in other orbits
start = dt.datetime(year=2011, month=4, day=11, hour=5, minute=0)
end = dt.datetime(year=2011, month=4, day=11, hour=5, minute=30)
data_length = end - start

#############################################################
##################### FINDING ORBITS ########################
#############################################################

# Set the number of orbits either side
number_of_orbits = 3
approx_orbit_period = dt.timedelta(hours=12)

apoapsis_altitudes, apoapsis_times = trajectory.Get_All_Apoapsis_In_Range(
    start - number_of_orbits * approx_orbit_period,
    start + number_of_orbits * approx_orbit_period,
    metakernel,
    number_of_orbits_to_include=number_of_orbits * 2 + 1,
)

# Determine how far before apoapsis our start time is.
middle_index = len(apoapsis_times) // 2

middle_apoapsis_time = apoapsis_times[middle_index]
middle_apoapsis_altitude = apoapsis_altitudes[middle_index]


middle_data = mag.StripData(data, start, end)
# Converting to MSM
middle_data = mag.MSO_TO_MSM(middle_data)
# Accounting for solar wind aberration angle
middle_data = mag.AdjustForAberration(middle_data)

# Create new column in data for minutes before apoapsis
minutes_before_apoapsis = []

for date in middle_data["date"]:
    minutes_before_apoapsis.append((middle_apoapsis_time - date).total_seconds() / 60)

middle_data["minutes before apoapsis"] = minutes_before_apoapsis

minutes_before = middle_data["minutes before apoapsis"][0]


data_groups = []
for apoapsis_time in apoapsis_times:

    start_time = apoapsis_time - dt.timedelta(minutes=minutes_before)
    end_time = start_time + data_length

    new_data = mag.StripData(
        data,
        start_time,
        end_time,
    )
    # Converting to MSM
    new_data = mag.MSO_TO_MSM(new_data)
    # Accounting for solar wind aberration angle
    new_data = mag.AdjustForAberration(new_data)

    new_data["minutes before apoapsis"] = minutes_before_apoapsis

    data_groups.append(new_data)


####################################################
###################### PLOTTING ####################
####################################################

fig, axes = plt.subplots(len(data_groups), 1, sharex=True)

for i, orbit_data in enumerate(data_groups):

    ax = axes[i]

    if i == middle_index:
        colour = "orange"
    else:
        colour = "black"
        ax.plot(
            data_groups[middle_index]["minutes before apoapsis"],
            data_groups[middle_index]["mag_total"],
            color="orange",
            lw=0.8,
        )

    ax.plot(
        orbit_data["minutes before apoapsis"],
        orbit_data["mag_total"],
        color=colour,
        lw=0.8,
        label=f"{orbit_data['date'].iloc[0].strftime("%Y-%m-%d %H:%M:%S")} to {orbit_data['date'].iloc[-1].strftime("%Y-%m-%d %H:%M:%S")}",
    )

    ax.set_xlim(minutes_before, np.min(orbit_data["minutes before apoapsis"]))
    ax.legend()

    ax.set_xmargin(0)
    ax.tick_params("x", which="major", direction="inout", length=16, width=1)
    ax.tick_params("x", which="minor", direction="inout", length=8, width=0.8)

    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(10))

axes[-1].set_xlabel("Minutes before apoapsis")
fig.text(0.06, 0.5, "|B| [nT]", ha="center", va="center", rotation="vertical")

fig.suptitle(
    f"Consecutive Orbits From {data_groups[0]['date'][0]} to {data_groups[-1]['date'][0]}"
)

plt.show()
