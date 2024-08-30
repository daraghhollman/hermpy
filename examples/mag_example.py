import datetime as dt

import matplotlib.pyplot as plt

from MercuryTools import mag

root_dir = "/home/daraghhollman/Main/data/mercury/messenger/mag/"

# Loading data, downloaded from PDS
data = mag.Load_Messenger(
    [
        root_dir + "2012/01_JAN/MAGMSOSCIAVG12001_01_V08.TAB",
        root_dir + "2012/01_JAN/MAGMSOSCIAVG12002_01_V08.TAB",
    ]
)

start = dt.datetime(year=2012, month=1, day=1, hour=10)
end = dt.datetime(year=2012, month=1, day=2, hour=14)

# Isolating only a particular portion of the files
data = mag.StripData(data, start, end)

# Converting to MSM
data = mag.MSO_TO_MSM(data)

# Accounting for solar wind aberration angle
data = mag.AdjustForAberration(data)

"""
This data object is a Pandas DataFrame, and has the following columns:

date:  a datetime object of the time of the measurement
frame: the current coordinate system
eph_x: the x coordinate of the spacecraft (km)
eph_y: the y coordinate of the spacecraft (km)
eph_z: the z coordinate of the spacecraft (km)
range: the distance of the spacecraft from Mercury (km)
mag_x: the magnetic field strength in x (nt)
mag_y: the magnetic field strength in y (nt)
mag_z: the magnetic field strength in z (nt)
mag_total: the total magnetic field strength (nt)
"""

# This data can then be plotted using external libraries
fig, ax = plt.subplots()

ax.plot(data["date"], data["mag_total"])

plt.show()
