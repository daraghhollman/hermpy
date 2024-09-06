import datetime as dt

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import spiceypy as spice

from hermean_toolbelt import mag, plotting_tools, trajectory

mpl.rcParams["font.size"] = 14

#################### LOADING FILES #########################
root_dir = "/home/daraghhollman/Main/data/mercury/messenger/mag/"

metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"

data = mag.Load_Messenger(
    [
        root_dir + "2013/01_JAN/MAGMSOSCIAVG13001_01_V08.TAB",
        root_dir + "2013/01_JAN/MAGMSOSCIAVG13002_01_V08.TAB",
        root_dir + "2013/01_JAN/MAGMSOSCIAVG13003_01_V08.TAB",
        root_dir + "2013/01_JAN/MAGMSOSCIAVG13004_01_V08.TAB",
    ]
)

# Define the time segement we want to look at
# We can convert this to minutes before / after apoapsis
# to look at the same time in other orbits
start = dt.datetime(year=2013, month=1, day=3, hour=9)
end = dt.datetime(year=2013, month=1, day=3, hour=10)

midpoint = start + (end - start) / 2

# First we find the apoapsis nearest to the center of our data
centre_apoapsis_time, centre_apoapsis_altitude = trajectory.Get_Nearest_Apoapsis(
    midpoint, metakernel, time_delta=dt.timedelta(minutes=30)
)

number_of_orbits = 2
approx_orbit_period = dt.timedelta(hours=12)

# Loop through all orbits at 5 second resolution
apoapsis_times = []
for i in range(-number_of_orbits, number_of_orbits + 1, 1):
    apoapsis_time, _ = trajectory.Get_Nearest_Apoapsis(
        centre_apoapsis_time + i * approx_orbit_period,
        metakernel,
        time_delta=dt.timedelta(seconds=5),
    )

    print(f"Apoapsis found at: {apoapsis_time}")

    apoapsis_times.append(apoapsis_time)


# convert to time after apoapsis
# a negative time after means the time is before
print(start)
print(apoapsis_times[2])
start_time_after_apoapsis = apoapsis_times[2] - start

print(start_time_after_apoapsis)
