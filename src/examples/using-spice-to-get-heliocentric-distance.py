"""
Using SPICE to get MESSENGER's heliocentric distance
====================================================

In this example, we show how ``hermpy.net.ClientSPICE`` can be used to
query the position of MESSENGER over a long duration of time.
"""

import datetime as dt

import spiceypy as spice
import numpy as np
from sunpy.time import TimeRange
import matplotlib.pyplot as plt
import astropy.units as u

# %%
# ``hermpy.net`` introduces a client to handle the caching and fetching of
# SPICE kernels.
#
# There are default inclusions, which provide enough information for
# referencing the positions of planets and the sun, but not MESSENGER's
# position.
from hermpy.net import ClientSPICE

spice_client = ClientSPICE()

# %%
# Adding kernels
# --------------
# Kernels can be added to the SPICE client through updating the
# ``KERNEL_LOCATIONS`` dictionary. ``KERNEL_LOCATIONS`` expects the format seen
# below, with a base url (``BASE``), a subdirectory (``DIRECTORY``), and a list
# of filepatterns to search for (``PATTERNS``). The outermost key is purely to
# help describe the addition and is not used internally. Character wildcards
# are represented as '?'.
#
# Here we need to add MESSENGER mission kernels.
spice_client.KERNEL_LOCATIONS.update(
    {
        "MESSENGER": {
            "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
            "DIRECTORY": "pds/data/mess-e_v_h-spice-6-v1.0/messsp_1000/data/spk/",
            "PATTERNS": ["msgr_??????_??????_??????_od431sc_2.bsp"],
        },
    }
)

# %%
# Loading kernels with ``spiceypy`` and getting solar distances
# -------------------------------------------------------------
# We open a context in which we load kernels from ``ClientSPICE``. For more details
# see the ``spiceypy`` documentation. We can use SunPy's ``TimeRange`` and
# split based on some time resolution to get a list of query times.
time_resolution = dt.timedelta(days=1)
time_range = TimeRange("2004-09-12", "2015-04-30")
times = [
    t.start.to_datetime(leap_second_strict="warn")
    for t in time_range.window(cadence=time_resolution, window=time_resolution)
]

with spice_client.KernelPool():
    ets = spice.datetime2et(times)
    positions, _ = spice.spkpos("MESSENGER", ets, "J2000", "NONE", "SUN")

    positions *= u.km

    distances = np.linalg.norm(positions, axis=1)

    distances = distances.to(u.au)

    print(distances)

# %%
# Plotting MESSENGER's solar distance
# -----------------------------------
_, ax = plt.subplots()

ax.plot(times, distances, color="black")

ax.set(ylabel="MESSENGER Solar Distance [au]")

plt.show()
