import datetime as dt

import matplotlib.pyplot as plt
import numpy as np

import hermpy.fips as fips
import hermpy.plotting_tools as plotting_tools

# import hermpy.boundary_crossings as boundary_crossings


metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"
data = fips.Load_Messenger(
    [
        "/home/daraghhollman/Main/data/mercury/messenger/FIPS/2011/09_SEP/FIPS_R2011269CDR_V3.TAB"
    ]
)

start = dt.datetime(year=2011, month=9, day=26, hour=12, minute=5)
stop = dt.datetime(year=2011, month=9, day=26, hour=13, minute=15)
data = fips.Strip_Data(data, start, stop)

# We transpose to place the time axis along x
z = np.transpose(data["proton_energies"])

# When using flat shading for pcolormesh, we require that the
# arrays defining the axes be one larger than the data. This is
# to define the last edge.
# We can achieve this simply by removing the last column of the
# data.
z = np.delete(z, -1, 1)

fig, ax = plt.subplots()

fips_mesh = ax.pcolormesh(data["dates"], np.arange(0, 64), z)
plt.colorbar(fips_mesh)

plotting_tools.Add_Tick_Ephemeris(ax, metakernel)

plt.show()
