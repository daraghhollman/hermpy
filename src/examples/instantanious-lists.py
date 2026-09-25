"""
Comparing event lists with data
===============================

In this example, we showcase how a list of events can be merged with MESSENGER
MAG data for comparison.
"""

import datetime as dt
from pathlib import Path

import matplotlib.pyplot as plt
import requests
from astropy.table import Table
from astropy.time import Time
from matplotlib.dates import DateFormatter
from sunpy.time import TimeRange

from hermpy.data import (
    add_field_magnitude,
    parse_messenger_mag,
    rotate_to_aberrated_coordinates,
)
from hermpy.net import ClientMESSENGER, ClientSPICE
from hermpy.utils import Constants as c

# %%
# Downloading and parsing MESSENGER MAG data
# ------------------------------------------
# For step-by-step instructions on how to download MESSENGER data with hermpy,
# see `here <plot_one_orbit_of_messenger_mag.html>`_.
#
start_time = "2012-04-01 07:00"
time_range = TimeRange(start_time, dt.timedelta(minutes=40))

downloader = ClientMESSENGER()
downloader.query(time_range, "MAG 1s")
files = downloader.fetch()

data = parse_messenger_mag(files, time_range)
data = add_field_magnitude(data)

data["X MSM"] = data["X MSO"]
data["Y MSM"] = data["Y MSO"]
data["Z MSM"] = data["Z MSO"] - c.DIPOLE_OFFSET.to(c.MERCURY_RADIUS)

spice_client = ClientSPICE()

with spice_client.KernelPool():
    data = rotate_to_aberrated_coordinates(data)

# %%
# Downloading a crossing list
# ---------------------------
# Here, we download the MESSENGER magnetospheric boundary crossing list by
# `Hollman et al. (2026) <https://doi.org/10.1029/2025JH000921>`_.
#
# We rename the 'Time' column to 'UTC' to match the time column in our data.

url = "https://zenodo.org/records/21392216/files/hollman_2026_crossing_list.csv?download=1"
crossing_list_path = Path("./hollman_2026_crossing_list.csv")

# If the file doesn't exist, download it
if not crossing_list_path.exists():
    response = requests.get(url)
    with open(crossing_list_path, "wb") as file:
        file.write(response.content)

# Read as astropy Table, and rename columns
crossings = Table.read(crossing_list_path)
crossings.rename_column("Time", "UTC")
crossings["UTC"] = Time(crossings["UTC"])

# Filter to only the crossings within our data
crossings: Table = crossings[
    (crossings["UTC"] >= time_range.start) & (crossings["UTC"] <= time_range.end)
]

# %%
# Plot with the data
# ------------------
# For this example, we showcase the crossings plotted as vertical lines over
# the data.

fig, ax = plt.subplots(figsize=(12, 4))

# Plot the |B| trace of MAG
ax.plot(data["UTC"].to_datetime(), data["|B|"], color="black", lw=0.5)

for crossing in crossings:
    # Add a vertical line where each crossing is
    ax.axvline(
        crossing["UTC"].to_datetime(),
        color="indianred",
        ls="dashed",
    )


ax.set_ylabel("|B| [nT]")
ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d\n%H:%M"))

plt.show()
