# Multi-Panel Plotting

This example demonstrates how to construct multi-panel time series plots using
`hermpy.plotting.MultiPanel`. We fetch one hour of MESSENGER MAG and FIPS data,
parse them into their respective data structures, and progressively build up a
combined plot.

## Table of Contents

* [Prerequisites](#prerequisites)
* [Fetching data](#fetching-data)
* [Parsing data](#parsing-data)
* [Preparing the MAG table](#preparing-the-mag-table)
* [Plotting a single panel](#plotting-a-single-panel)
* [Building a multi-panel plot](#building-a-multi-panel-plot)
* [Extending a multi-panel plot](#extending-a-multi-panel-plot)

---

## Prerequisites

```python
import xarray as xr
from astropy.table import QTable
from sunpy.time import TimeRange
from hermpy.data import parse_messenger_fips, parse_messenger_mag
from hermpy.net import ClientMESSENGER
from hermpy.plotting import MultiPanel, SpectrogramPanel, TimeseriesPanel
```

---

## Fetching data

We use `hermpy.net.ClientMESSENGER` to download MAG and FIPS data for a
one-hour window. For a full walkthrough of the download client, see the
downloading data example.

```python
c = ClientMESSENGER()
time_range = TimeRange("2011-06-01T00:00", "2011-06-01T01:00")

c.query(time_range, "MAG")
mag_file_paths = c.fetch()

c.query(time_range, "FIPS")
fips_file_paths = c.fetch()
```

!!! note
    `ClientMESSENGER.query()` stages the request and `ClientMESSENGER.fetch()`
    performs the download, returning a list of local file paths.

    Calls are intentionally separated so that you can inspect or filter the query
    results before committing to a download.

---

## Parsing data

MAG data is returned as an `astropy.table.QTable` — a quantity-aware table
suited to time series with physical units.

FIPS data is returned as an `xarray.Dataset`, which represents the 2-D
energy-time spectrogram.

```python
mag_data: QTable = parse_messenger_mag(mag_file_paths, time_range)
fips_data: xr.Dataset = parse_messenger_fips(fips_file_paths, time_range)
```

---

## Preparing the MAG table

MESSENGER MAG files contain both magnetic field components and ephemeris
columns. Because these columns carry different physical units they cannot share
a single y-axis, so passing the full table to a
`hermpy.plotting.TimeseriesPanel` would raise an error.

We therefore trim the table to only the columns we want to plot:

```python
mag_data.keep_columns(["UTC", "Bx", "By", "Bz"])
```

!!! warning
    `astropy.table.Table.keep_columns()` modifies the table **in place**.

    If you need the full table later, take a copy first with:

    ```python
    mag_data.copy()
    ```

---

## Plotting a single panel

Each `hermpy.plotting.TimeseriesPanel` (and `hermpy.plotting.SpectrogramPanel`)
has a `.plot()` method that returns a `(figure, axes)` pair and calls
`matplotlib.pyplot.show()` by default:

```python
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
```

To defer rendering — useful when embedding a panel inside a larger figure —
pass `show=False` and call `matplotlib.pyplot.show()` yourself at a later
point.

---

## Building a multi-panel plot

The real power of Panel objects is that they compose naturally using the
addition operator. Adding two panels returns a `hermpy.plotting.MultiPanel`:

```python
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
```

---

## Extending a multi-panel plot

`hermpy.plotting.MultiPanel` objects are themselves composable. You can
concatenate two `MultiPanel` objects, or append an individual panel to an
existing one, using `+=`:

```python
# Double up: stack the same two panels again below the first two.
multipanel += multipanel

# Append a single panel at the bottom.
multipanel += mag_panel

multipanel.plot()
```
