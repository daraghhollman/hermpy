"""
Creating Multi-panel plots with hermpy
======================================

This example demonstrates how to construct multi-panel time series plots using
``hermpy.plotting.MultiPanel``. We fetch one hour of MESSENGER MAG and FIPS data,
parse them into their respective data structures, and progressively build up a
combined plot.
"""

import xarray as xr
from astropy.table import QTable
from sunpy.time import TimeRange

from hermpy.data import parse_messenger_fips, parse_messenger_mag
from hermpy.net import ClientMESSENGER
from hermpy.plotting import MultiPanel, SpectrogramPanel, TimeseriesPanel

# %%
# First we must get some data. Here we fetch MESSENGER MAG and FIPS data for a
# particular time range.
#
# We use ``hermpy.net.ClientMESSENGER`` to download MAG and FIPS data for a
# one-hour window. See `here`_ for more details.
#
# .. _here: download_data.html
c = ClientMESSENGER()
time_range = TimeRange("2011-06-01T00:00", "2011-06-01T01:00")

c.query(time_range, "MAG")
mag_file_paths = c.fetch()

c.query(time_range, "FIPS")
fips_file_paths = c.fetch()

# %%
# We use Astropy's Quantity Table (QTable) for time series data, and Xarray's
# Dataset for 2D data. These custom parsers are included in ``hermpy.data``,
# but may be replaced in later versions.
mag_data: QTable = parse_messenger_mag(mag_file_paths, time_range)
fips_data: xr.Dataset = parse_messenger_fips(fips_file_paths, time_range)

# %%
print(mag_data)

# %%
print(fips_data)

# %%
# As MESSENGER MAG data contains both ephemeris and magnetic field data,
# adding this data as it is to a Panel object will result in an error, as the
# columns (excluding the time column) have multiple units, and hence can't be
# represented on the same axis.
#
# We therefore need to shorten this table to just the columns we want in this
# Panel object.
mag_data.keep_columns(["UTC", "Bx", "By", "Bz"])

# %%
# ``hermpy`` provides the ``Panel`` abstract base class, which is expanded upon
# in ``TimeseriesPanel`` and ``SpectrogramPanel``.
#
# We use a ``TimeseriesPanel`` as this matches the data type.
#
# Each panel has a built-in plot function which returns a ``Figure`` and
# ``Axes`` for that panel in isolation. ``plt.show()`` is called within this
# function however uou can defer rendering until later by setting
# ``.plot(show=False)``, and then using ``plt.show()`` at a later point.
mag_panel = TimeseriesPanel(mag_data)
fig, ax = mag_panel.plot()

# %%
# Plotting with more than one panel
# ---------------------------------
# However, the power in Panel objects comes when we go to construct multipanel
# plots. We can combine Panel objects to construct a multi-panel plot by simply
# adding them.
#
# Lets make a second panel where we plot the FIPS data. We can combine the two
# using the addition operator.
proton_flux = fips_data["Proton Flux"]
fips_panel = SpectrogramPanel(proton_flux)

multipanel: MultiPanel = mag_panel + fips_panel
fig, axes = multipanel.plot()

# %%
# You can also add multipanels to the same effect, and panels can also be added
# to multipanel objects.
multipanel += multipanel
multipanel.plot()

# %%
multipanel += mag_panel
multipanel.plot()
