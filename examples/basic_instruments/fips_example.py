import datetime as dt

import matplotlib as mpl
import matplotlib.colors as mpl_colors
import matplotlib.pyplot as plt
import numpy as np
import spiceypy as spice

import hermpy.boundary_crossings as boundary_crossings
import hermpy.fips as fips
import hermpy.plotting_tools as plotting_tools

mpl.rcParams["font.size"] = 18

metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"
spice.furnsh(metakernel)
philpott_crossings = boundary_crossings.Load_Crossings(
    "/home/daraghhollman/Main/Work/mercury/philpott_2020_reformatted.csv"
)

start = dt.datetime(year=2013, month=8, day=19, hour=12)
stop = dt.datetime(year=2013, month=8, day=22, hour=21)

data = fips.Load_Between_Dates("/home/daraghhollman/Main/data/mercury/messenger/FIPS/", start, stop, strip=True)

# We transpose to place the time axis along x
protons = np.transpose(data["proton_energies"])
heavy_ions = np.transpose(data["ve_energies"] - data["proton_energies"])

# When using flat shading for pcolormesh, we require that the
# arrays defining the axes be one larger than the data. This is
# to define the last edge.
# We can achieve this simply by removing the last column of the
# data.
protons = np.delete(protons, -1, 1)
heavy_ions = np.delete(heavy_ions, -1, 1)

fips_calibration = fips.Get_Calibration()

fig, axes = plt.subplots(2, 1, sharex=True)

cmap = "plasma"
protons_mesh = axes[0].pcolormesh(
    data["dates"], fips_calibration, protons, norm=mpl_colors.LogNorm(), cmap=cmap
)
heavy_ions_mesh = axes[1].pcolormesh(data["dates"], fips_calibration, heavy_ions, norm=mpl_colors.LogNorm(), cmap=cmap)

colorbar_label = "Diff. Energy Flux\n[(keV/e)$^{-1}$ sec$^{-1}$ cm$^{-2}$]"
plt.colorbar(protons_mesh, ax=axes[0], label="Proton " + colorbar_label)
plt.colorbar(protons_mesh, ax=axes[1], label="Heavy Ion " + colorbar_label)

plotting_tools.Add_Tick_Ephemeris(axes[1], {"date", "hours", "minutes", "range", "latitude", "local time"})

for ax in axes:
    ax.set_ylabel("E/Q [keV/Q]")
    ax.set_yscale("log")
    boundary_crossings.Plot_Crossing_Intervals(ax, start, stop, philpott_crossings, color="black", height=1.1)

plt.show()
