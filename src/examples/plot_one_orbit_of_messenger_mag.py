"""
Plotting an orbit of MESSENGER MAG
==================================

In this example, we showcase the downloading, and minimal analysis required to
plot a single orbit of MESSENGER MAG data.
"""

import datetime as dt

import matplotlib.pyplot as plt
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
# Downloading data
# ----------------
# We use ``hermpy.net.ClientMESSENGER`` to access MESSENGER data. See `here <download_data.html>`_
# for more details.
#
start_time = "2012-04-01 05:00"
time_range = TimeRange(start_time, dt.timedelta(hours=8))

downloader = ClientMESSENGER()
downloader.query(time_range, "MAG 60s")
files = downloader.fetch()

# %%
# Parsing the data
# ----------------
# The above code-block downloads MESSENGER MAG data in their raw ``.TAB``
# format. ``hermpy.data`` implements useful routines to parse these data into
# an Astropy `QTable
# <https://docs.astropy.org/en/stable/api/astropy.table.QTable.html#astropy.table.QTable>`_.
#
data = parse_messenger_mag(files, time_range)
data = add_field_magnitude(data)

print(data)

# %%
# Converting to MSM Coordinates
# --------------------------------
# Note that these data contain the position and magnetic field values in
# Mercury-Solar-Orbital (MSO) coordinates. We should convert to
# Mercury-Solar-Magnetospheric (MSM), where the origin is co-situated with
# Mercury's dipole. We can do this by adjusting the z-axis by the dipole
# offset: 479 km (~0.2 R) [1]_.
#
# .. note::
#     Note that while we will not plot any position data in this
#     example, we felt it fit to include these instructions here.
#
data["X MSM"] = data["X MSO"]
data["Y MSM"] = data["Y MSO"]
data["Z MSM"] = data["Z MSO"] - c.DIPOLE_OFFSET.to(c.MERCURY_RADIUS)


# %%
# Aberrating the reference frame
# ------------------------------
# Additionally, these coordinate systems point the x-axis
# towards the Sun. Often it is also useful to rotate (or 'aberrate') the
# reference frame such that the x-axis points into the solar wind flow.
# The convention to denote aberrated frames is by using
# primed-notation: ``'``.
#
# Aberration is a calculation based on the velocity of Mercury, and an assumed
# solar wind velocity of 400 km/s. To determine these, we must load some spice
# kernels. The built-in kernels to ``hermpy.net.ClientSPICE`` are sufficient to
# compute this. See `here <spice.html>`_ for more details.
#
spice_client = ClientSPICE()

with spice_client.KernelPool():
    data = rotate_to_aberrated_coordinates(data)

print("Columns:")
for column in data.columns:
    print(column)


# %%
# Plotting
# --------
#
# Here we use colours from a 7-colour palette by Wong (2023) [2]_
#
# Additionally, it is nice to set a custom ``DateFormater`` to be
# less ambiguous about the y-ticks.
#
fig, ax = plt.subplots(figsize=(12, 4))

vars = ["|B|", "Bx'", "By'", "Bz'"]
colours = ["black", "#D55E00", "#009E73", "#0072B2"]

for var, colour in zip(vars, colours):
    ax.plot(data["UTC"].to_datetime(), data[var].value, color=colour, label=var)

ax.legend()
ax.margins(x=0)
ax.set_ylabel("[nT]")
ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d\n%H:%M"))

plt.show()

# %%
# References
# ----------
#
# .. [1] Johnson et al. (2012),
#        *MESSENGER observations of Mercury's magnetic field structure*,
#        Journal of Geophysical Research (Planets),
#        https://doi.org/10.1029/2012JE004217
#
# .. [2] Wong (2023),
#        *Points of view: Colorblindness*,
#        Nature Methods,
#        https://doi.org/10.1038/nmeth.1618
