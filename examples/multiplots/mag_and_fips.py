import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.ticker as mpl_ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

from hermpy import boundaries, fips, mag, utils, plotting

start = dt.datetime(year=2013, month=4, day=28, hour=16, minute=50)
stop = dt.datetime(year=2013, month=4, day=28, hour=17, minute=15)

mag_data = mag.Load_Between_Dates(utils.User.DATA_DIRECTORIES["MAG"], start, stop)
fips_data = fips.Load_Between_Dates(utils.User.DATA_DIRECTORIES["FIPS"], start, stop)

crossings = boundaries.Load_Crossings(utils.User.CROSSING_LISTS["Philpott"])

# We transpose to place the time axis along x
protons = np.transpose(fips_data["proton_energies"])

# When using flat shading for pcolormesh, we require that the
# arrays defining the axes be one larger than the data. This is
# to define the last edge.
# We can achieve this simply by removing the last column of the
# data.
protons = np.delete(protons, -1, 1)

fips_calibration = fips.Get_Calibration()


fig, axes = plt.subplots(2, 1, sharex=True)
(mag_axis, fips_axis) = axes

mag_axis.plot(mag_data["date"], mag_data["Bx"], color="#DC267F", label="Bx")
mag_axis.plot(mag_data["date"], mag_data["By"], color="#FFB000", label="By")
mag_axis.plot(mag_data["date"], mag_data["Bz"], color="#648FFF", label="Bz")
mag_axis.plot(mag_data["date"], mag_data["|B|"], color="black", label="|B|")

mag_axis.set_ylabel("Magnetic Field Strength [nT]")
mag_axis.legend()

mag_divider = make_axes_locatable(mag_axis)
fips_divider = make_axes_locatable(fips_axis)

cax = fips_divider.append_axes("right", size="3%", pad=0.2)
_ = mag_divider.append_axes("right", size="3%", pad=0.2)
_.set_axis_off()

protons_mesh = fips_axis.pcolormesh(
    fips_data["dates"], fips_calibration, protons, norm="log", cmap="plasma"
)

colorbar_label = "Diff. Energy Flux\n[(keV/e)$^{-1}$ sec$^{-1}$ cm$^{-2}$]"
plt.colorbar(protons_mesh, cax=cax, label="Proton " + colorbar_label)

mag_axis.xaxis.set_minor_locator(mpl_ticker.AutoMinorLocator())
mag_axis.yaxis.set_minor_locator(mpl_ticker.AutoMinorLocator())

mag_axis.axhline(0, color="grey", ls="dotted")

fips_axis.set_ylabel("E/Q [keV/Q]")
fips_axis.set_yscale("log")
fips_axis.xaxis.set_minor_locator(mpl_ticker.AutoMinorLocator())
plotting.Add_Tick_Ephemeris(fips_axis)

for ax in axes:
    ax.margins(0)
    boundaries.Plot_Crossing_Intervals(
        ax, start, stop, crossings, color="black", height=1.1
    )

plt.show()
