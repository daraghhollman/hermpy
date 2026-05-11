Multi-Panel Plotting
====================

This example demonstrates how to construct multi-panel time series plots using
:class:`hermpy.plotting.MultiPanel`. We fetch one hour of MESSENGER MAG and
FIPS data, parse them into their respective data structures, and progressively
build up a combined plot.

.. contents:: On this page
   :local:
   :depth: 2


Prerequisites
-------------

.. code-block:: python

   import xarray as xr
   from astropy.table import QTable
   from sunpy.time import TimeRange
   from hermpy.data import parse_messenger_fips, parse_messenger_mag
   from hermpy.net import ClientMESSENGER
   from hermpy.plotting import MultiPanel, SpectrogramPanel, TimeseriesPanel


Fetching data
-------------

We use :class:`~hermpy.net.ClientMESSENGER` to download MAG and FIPS data for
a one-hour window. For a full walkthrough of the download client, see
:doc:`/examples/downloading_data`.

.. code-block:: python

   c = ClientMESSENGER()
   time_range = TimeRange("2011-06-01T00:00", "2011-06-01T01:00")

   c.query(time_range, "MAG")
   mag_file_paths = c.fetch()

   c.query(time_range, "FIPS")
   fips_file_paths = c.fetch()

.. note::

   :meth:`~hermpy.net.ClientMESSENGER.query` stages the request and
   :meth:`~hermpy.net.ClientMESSENGER.fetch` performs the download, returning
   a list of local file paths. Calls are intentionally separated so that you
   can inspect or filter the query results before committing to a download.


Parsing data
------------

MAG data is returned as an :class:`astropy.table.QTable` — a quantity-aware
table suited to time series with physical units. FIPS data is returned as an
:class:`xarray.Dataset`, which represents the 2-D energy-time spectrogram.

.. code-block:: python

   mag_data: QTable = parse_messenger_mag(mag_file_paths, time_range)
   fips_data: xr.Dataset = parse_messenger_fips(fips_file_paths, time_range)


Preparing the MAG table
------------------------

MESSENGER MAG files contain both magnetic field components and ephemeris
columns. Because these columns carry different physical units they cannot share
a single y-axis, so passing the full table to a
:class:`~hermpy.plotting.TimeseriesPanel` would raise an error. We therefore
trim the table to only the columns we want to plot:

.. code-block:: python

   mag_data.keep_columns(["UTC", "Bx", "By", "Bz"])

.. warning::

   :meth:`~astropy.table.Table.keep_columns` modifies the table **in place**.
   If you need the full table later, take a copy first with
   ``mag_data.copy()``.


Plotting a single panel
-----------------------

Each :class:`~hermpy.plotting.TimeseriesPanel` (and
:class:`~hermpy.plotting.SpectrogramPanel`) has a
:meth:`~hermpy.plotting.TimeseriesPanel.plot` method that returns a
``(figure, axes)`` pair and calls :func:`matplotlib.pyplot.show` by default:

.. exec_code::

   import xarray as xr
   from sunpy.time import TimeRange
   from hermpy.data import parse_messenger_fips, parse_messenger_mag
   from hermpy.net import ClientMESSENGER
   from hermpy.plotting import TimeseriesPanel

   c = ClientMESSENGER()
   time_range = TimeRange("2011-06-01T00:00", "2011-06-01T01:00")

   c.query(time_range, "MAG")
   mag_data = parse_messenger_mag(c.fetch(), time_range)
   mag_data.keep_columns(["UTC", "Bx", "By", "Bz"])

   mag_panel = TimeseriesPanel(mag_data)
   fig, ax = mag_panel.plot(show=False)

.. plot::

   import xarray as xr
   from sunpy.time import TimeRange
   from hermpy.data import parse_messenger_fips, parse_messenger_mag
   from hermpy.net import ClientMESSENGER
   from hermpy.plotting import TimeseriesPanel

   c = ClientMESSENGER()
   time_range = TimeRange("2011-06-01T00:00", "2011-06-01T01:00")

   c.query(time_range, "MAG")
   mag_data = parse_messenger_mag(c.fetch(), time_range)
   mag_data.keep_columns(["UTC", "Bx", "By", "Bz"])

   mag_panel = TimeseriesPanel(mag_data)
   fig, ax = mag_panel.plot(show=False)

To defer rendering — useful when embedding a panel inside a larger figure —
pass ``show=False`` and call :func:`matplotlib.pyplot.show` yourself at a
later point.


Building a multi-panel plot
----------------------------

The real power of Panel objects is that they compose naturally using the
addition operator. Adding two panels returns a
:class:`~hermpy.plotting.MultiPanel`:

.. exec_code::

   import xarray as xr
   from sunpy.time import TimeRange
   from hermpy.data import parse_messenger_fips, parse_messenger_mag
   from hermpy.net import ClientMESSENGER
   from hermpy.plotting import MultiPanel, SpectrogramPanel, TimeseriesPanel

   c = ClientMESSENGER()
   time_range = TimeRange("2011-06-01T00:00", "2011-06-01T01:00")

   c.query(time_range, "MAG")
   mag_data = parse_messenger_mag(c.fetch(), time_range)
   mag_data.keep_columns(["UTC", "Bx", "By", "Bz"])

   c.query(time_range, "FIPS")
   fips_data = parse_messenger_fips(c.fetch(), time_range)

   mag_panel = TimeseriesPanel(mag_data)
   fips_panel = SpectrogramPanel(fips_data["Proton Flux"])

   multipanel: MultiPanel = mag_panel + fips_panel
   fig, axes = multipanel.plot(show=False)

.. plot::

   import xarray as xr
   from sunpy.time import TimeRange
   from hermpy.data import parse_messenger_fips, parse_messenger_mag
   from hermpy.net import ClientMESSENGER
   from hermpy.plotting import MultiPanel, SpectrogramPanel, TimeseriesPanel

   c = ClientMESSENGER()
   time_range = TimeRange("2011-06-01T00:00", "2011-06-01T01:00")

   c.query(time_range, "MAG")
   mag_data = parse_messenger_mag(c.fetch(), time_range)
   mag_data.keep_columns(["UTC", "Bx", "By", "Bz"])

   c.query(time_range, "FIPS")
   fips_data = parse_messenger_fips(c.fetch(), time_range)

   mag_panel = TimeseriesPanel(mag_data)
   fips_panel = SpectrogramPanel(fips_data["Proton Flux"])

   multipanel: MultiPanel = mag_panel + fips_panel
   fig, axes = multipanel.plot(show=False)


Extending a multi-panel plot
-----------------------------

:class:`~hermpy.plotting.MultiPanel` objects are themselves composable. You
can concatenate two ``MultiPanel`` objects, or append an individual panel to an
existing one, using ``+=``:

.. code-block:: python

   # Double up: stack the same two panels again below the first two.
   multipanel += multipanel

   # Append a single panel at the bottom.
   multipanel += mag_panel

   multipanel.plot()

See also
--------

- :doc:`/examples/downloading_data` — fetching MESSENGER data with ``ClientMESSENGER``
- :doc:`/examples/index` — full examples gallery
- :class:`hermpy.plotting.MultiPanel` — API reference
- :class:`hermpy.plotting.TimeseriesPanel` — API reference
- :class:`hermpy.plotting.SpectrogramPanel` — API reference
