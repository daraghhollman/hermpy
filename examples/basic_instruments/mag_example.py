import datetime as dt

import matplotlib.pyplot as plt

from hermpy import mag
from hermpy.utils import User

start = dt.datetime(year=2011, month=3, day=24)
end = dt.datetime(year=2011, month=3, day=25)

# Isolating only a particular portion of the files
data = mag.Load_Between_Dates(
    User.DATA_DIRECTORIES["MAG_FULL"], start, end, average=None
)

# This data can then be plotted using external libraries such as matplotlib
fig, ax = plt.subplots()

ax.plot(data["date"], data["|B|"], color="black", label="|B|")
ax.plot(data["date"], data["Bx"], color="#DC267F", label="Bx")
ax.plot(data["date"], data["By"], color="#FFB000", label="By")
ax.plot(data["date"], data["Bz"], color="#648FFF", label="Bz")

ax.set_xlabel("Time")
ax.set_ylabel("Magnetic Field Strength [nT]")

ax.legend()

plt.show()
