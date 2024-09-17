import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates

import hermpy.fips as fips
import hermpy.plotting_tools as plotting_tools


metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"
data = fips.Load_Messenger([
    "/home/daraghhollman/Main/data/mercury/messenger/FIPS/2012/01_JAN/FIPS_R2012001CDR_V3.TAB"
])

start = 
end = 
fips.StripData()

# We squeeze the list of arrays to combine them into one array.
z = np.squeeze(data["proton_energies"])

# We transpose to place the time axis along x
z = np.transpose(z)

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
