"""
Using SPICE kernels with hermpy
===============================

In this example, we show how ``hermpy.net.ClientSPICE`` can be used to
download, access, and use SPICE kernels from multiple sources.
"""

import datetime as dt

import spiceypy as spice

# %%
# ``hermpy.net`` introduces a client to handle the caching and fetching of
# SPICE kernels.
#
# There are some default kernels included by default, but more can be added on
# the fly. If you feel your additions would make sense as permanent inclusion,
# please open a PR.
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
# Here we show an example of adding MESSENGER mission kernels, and a coordinate
# system kernel defined for the BepiColombo mission.
spice_client.KERNEL_LOCATIONS.update(
    {
        "MESSENGER Frames (tf)": {
            "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
            "DIRECTORY": "pds/data/mess-e_v_h-spice-6-v1.0/messsp_1000/data/fk/",
            "PATTERNS": ["msgr_dyn_v600.tf"],
        },
        "MESSENGER": {
            "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
            "DIRECTORY": "pds/data/mess-e_v_h-spice-6-v1.0/messsp_1000/data/spk/",
            "PATTERNS": ["msgr_??????_??????_??????_od431sc_2.bsp"],
        },
        "BepiColombo Frames": {
            "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
            "DIRECTORY": "pds/pds4/bc/bc_spice/spice_kernels/fk/",
            "PATTERNS": ["bc_sci_v12.tf"],
        },
    }
)

# %%
# Loading kernels with ``spiceypy``
# ---------------------------------
# We open a context in which we load kernels from ``ClientSPICE``. For more details
# see the ``spiceypy documentation.
with spice.KernelPool(spice_client.fetch()):
    et = spice.datetime2et(dt.datetime(2012, 6, 1))
    position, _ = spice.spkpos("MESSENGER", et, "BC_MSO_AB", "NONE", "Mercury")

    print(position)

# %%
# Loading kernels directly wit ``ClientSPICE``
# --------------------------------------------
# Equivalently (and often preferably), we define a context manager within
# ``ClientSPICE`` which extends the above. All that happens under the hood here
# is that the spice client performs the fetch, passes it to spice.KernelPool(),
# and yields the contextmanager.
with spice_client.KernelPool():
    et = spice.datetime2et(dt.datetime(2012, 6, 1))
    position, _ = spice.spkpos("MESSENGER", et, "BC_MSO_AB", "NONE", "Mercury")

    print(position)
