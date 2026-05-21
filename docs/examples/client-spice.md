# Using ClientSPICE to Manage SPICE Kernels

This example demonstrates how to use `ClientSPICE` from `hermpy.net` to fetch and manage SPICE kernels, and how to compute spacecraft positions using [spiceypy](https://spiceypy.readthedocs.io/en/main/).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setting up the client](#setting-up-the-client)
- [Adding custom kernels](#adding-custom-kernels)
- [Loading kernels and computing a position](#loading-kernels-and-computing-a-position)
  - [Using `spice.KernelPool` directly](#using-spicekernelpool-directly)
  - [Using `spice_client.KernelPool` (preferred)](#using-spice_clientkernelpool-preferred)
- [Complete example](#complete-example)

---

## Prerequisites

This example requires the following imports:

```python
import datetime as dt
import spiceypy as spice
from hermpy.net import ClientSPICE
```

---

## Setting up the client

`ClientSPICE` is a caching client that handles the fetching of SPICE kernels.
Instantiate one before opening any kernel context:

```python
spice_client = ClientSPICE()
```

A set of default kernels is bundled with `hermpy` and will be loaded
automatically. Additional kernels can be registered at any time by updating
`ClientSPICE.KERNEL_LOCATIONS`.

---

## Adding custom kernels

In this example, we will add position kernels for the MESSENGER mission, and
frame kernels from the BepiColombo mission.

The BepiColombo frames kernel exposes reference frames such as `BC_MSO_AB`.

```python
spice_client.KERNEL_LOCATIONS.update(
    {
        "MESSENGER": {
            "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
            "DIRECTORY": "pds/data/mess-e_v_h-spice-6-v1.0/messsp_1000/data/spk/",
            "PATTERNS": ["msgr_??????_??????_??????_od431sc_2.bsp"],
        },
        "BepiColombo Frames": {
            "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
            "DIRECTORY": "pds/pds4/bc/bc_spice/spice_kernels/fk/",
            "PATTERNS": ["bc_sci_v12.tf"],
        }
    }
)
```

`KERNEL_LOCATIONS` is a plain `dict`, so standard Python mapping operations
(`update`, direct key assignment, etc.) all work as expected.

---

## Loading kernels and computing a position

There are two equivalent ways to open a kernel context. Both approaches call
`ClientSPICE.fetch()` under the hood, which downloads any missing kernels and
returns a list of local paths.

### Using `spice.KernelPool` directly

You can pass the fetched kernel paths straight to `spiceypy.KernelPool`:

```python
with spice.KernelPool(spice_client.fetch()):
    et = spice.datetime2et(dt.datetime(2012, 6, 1))
    position, _ = spice.spkpos("MESSENGER", et, "BC_MSO_AB", "NONE", "Mercury")
    print(position)
```

```
[-1111.54790425 -4790.21635147 -2979.94219262]
```

`spiceypy.datetime2et` converts a standard `datetime.datetime` object to an
ephemeris time (ET) scalar, which is the time format expected by most SPICE
routines.

`spiceypy.spkpos` returns the position of the target body (`"MESSENGER"`)
relative to the observer (`"Mercury"`), expressed in the requested reference
frame (`"BC_MSO_AB"`), with no aberration correction (`"NONE"`). The second
return value — the one-way light time — is discarded with `_` here.

### Using `spice_client.KernelPool` (preferred)

`ClientSPICE.KernelPool()` is a convenience context manager that calls
`ClientSPICE.fetch()` and forwards the result to `spiceypy.KernelPool` for you:

```python
with spice_client.KernelPool():
    et = spice.datetime2et(dt.datetime(2012, 6, 1))
    position, _ = spice.spkpos("MESSENGER", et, "BC_MSO_AB", "NONE", "Mercury")
    print(position)
```

```
[-1111.54790425 -4790.21635147 -2979.94219262]
```

Both blocks produce identical output. The `spice_client.KernelPool()` form is
preferred because it keeps the fetch-and-load step implicit and avoids
repeating `spice_client.fetch()` at every call site.

---

## Complete example

```python
import datetime as dt
import spiceypy as spice
from hermpy.net import ClientSPICE

spice_client = ClientSPICE()

spice_client.KERNEL_LOCATIONS.update(
    {
        "BepiColombo Frames": {
            "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
            "DIRECTORY": "pds/pds4/bc/bc_spice/spice_kernels/fk/",
            "PATTERNS": ["bc_sci_v12.tf"],
        }
    }
)

with spice_client.KernelPool():
    et = spice.datetime2et(dt.datetime(2012, 6, 1))
    position, _ = spice.spkpos("MESSENGER", et, "BC_MSO_AB", "NONE", "Mercury")
    print(position)
```

```
[-1111.54790425 -4790.21635147 -2979.94219262]
```

This prints MESSENGER's position in kilometers in the (average) aberrated
Mercury-Solar-Orbital reference frame.

