"""
MESSENGER's orbit over the whole mission - simple view
========================================

A simplified version of the orbit overview, without colouring by region.
"""

from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import spiceypy as spice

from hermpy.net import ClientSPICE
from hermpy.utils import Constants as c
from hermpy.utils import download_files

# %%
# Orbit times
# -----------
# NAIF's orbit number file lists every orbit of the mission. An orbit starts
# at apoherm, and each line gives the orbit number, that time, and the time
# of the periherm within the orbit. The final orbit ends in the impact and
# has no periherm time, so it is skipped.
ORBNUM_URL = (
    "https://naif.jpl.nasa.gov/pub/naif/pds/data/mess-e_v_h-spice-6-v1.0/"
    "messsp_1000/extras/orbnum/msgr_040803_150430_150430_od431sc_2.orb"
)

[orbnum_path] = download_files([ORBNUM_URL])

orbit_numbers, apoherm_times, periherm_times = [], [], []

with open(orbnum_path) as orbnum_file:
    for line in orbnum_file:
        fields = line.split()

        if len(fields) != 15 or not fields[0].isdigit():
            continue

        orbit_numbers.append(int(fields[0]))
        apoherm_times.append(
            datetime.strptime(" ".join(fields[1:5]), "%Y %b %d %H:%M:%S")
        )
        periherm_times.append(
            datetime.strptime(" ".join(fields[6:10]), "%Y %b %d %H:%M:%S")
        )

# %%
# The four consecutive orbits are those of Figure 6 in Bowers et al. (2024),
# from 8 to 9 October 2011, from one apoherm to the apoherm after the
# fourth orbit.
FIRST_ORBIT = 410
SAMPLE_STEP = timedelta(minutes=1)

first_index = orbit_numbers.index(FIRST_ORBIT)
window_start = apoherm_times[first_index]
window_end = apoherm_times[first_index + 4]

sample_times = [
    window_start + i * SAMPLE_STEP
    for i in range(int((window_end - window_start) / SAMPLE_STEP) + 1)
]

# %%
# Positions
# ---------
# We need MESSENGER's trajectory, and the mission's frame kernel, which
# defines the MSO frame ``MSGR_MSO``.
spice_client = ClientSPICE()
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
    }
)


# %%
# Radial distance is in Mercury radii from the planet's centre. Local time
# is the angle from the anti-sunward direction in the MSO X-Y plane, so that
# 12 h is noon and 18 h is dusk. Latitude is measured from the MSO X-Y plane.
def mso_position(times: list[datetime]):
    position, _ = spice.spkpos(
        "MESSENGER", spice.datetime2et(times), "MSGR_MSO", "NONE", "MERCURY"
    )
    x, y, z = position.T

    radial_distance = np.linalg.norm(position, axis=1)
    local_time = (np.degrees(np.arctan2(y, x)) / 15 + 12) % 24
    latitude = np.degrees(np.arcsin(z / radial_distance))

    return radial_distance / c.MERCURY_RADIUS.to("km").value, local_time, latitude


with spice_client.KernelPool():
    apoherm_r, apoherm_lt, apoherm_lat = mso_position(apoherm_times)
    periherm_r, periherm_lt, periherm_lat = mso_position(periherm_times)
    sample_r, sample_lt, sample_lat = mso_position(sample_times)

    solar_position, _ = spice.spkpos(
        "MESSENGER", spice.datetime2et(apoherm_times), "J2000", "NONE", "SUN"
    )

AU_IN_KM = 149_597_870.7
heliocentric_distance = np.linalg.norm(solar_position, axis=1) / AU_IN_KM

# %%
# Plotting
# --------
# These helpers are shared by both figures.
APOHERM_COLOUR = "#A50F15"
PERIHERM_COLOUR = "#08306B"


def plot_apoherm_periherm(ax, times, apoherm, periherm, size=1.5):
    for times, values, colour, label in (
        (times[0], apoherm, APOHERM_COLOUR, "Apoherm"),
        (times[1], periherm, PERIHERM_COLOUR, "Periherm"),
    ):
        ax.plot(times, values, ".", color=colour, ms=size, label=label, zorder=3)


def finish_figure(axes, legend_columns, marker_scale=6):
    legend = axes[0].legend(
        loc="lower right",
        bbox_to_anchor=(1, 1),
        ncols=legend_columns,
        frameon=False,
        markerscale=marker_scale,
    )
    for handle in legend.get_lines():
        handle.set_linewidth(3)

    for ax, letter in zip(axes, "abcd"):
        ax.set_title(f"({letter})", loc="left", fontweight="bold", fontsize="medium")


def add_reference_lines(lt_axis, lat_axis):
    # Noon in local time, and the MSO equator in latitude.
    for ax, value in ((lt_axis, 12), (lat_axis, 0)):
        ax.axhline(value, color="grey", ls=":", lw=0.8, zorder=0)


R_LABEL = r"R [$R_M$]"
LT_SETTINGS = {"ylabel": "LT [hours]", "ylim": (0, 24), "yticks": range(0, 25, 6)}
LAT_SETTINGS = {"ylabel": "Lat [°]", "ylim": (-90, 90), "yticks": range(-90, 91, 45)}


# %%
# The whole mission
# -----------------
# Every orbit's apoherm and periherm is marked. In the first panel a black
# line joins the two, drawn faintly as there are too many orbits to tell the
# lines apart.
fig, axes = plt.subplots(4, 1, sharex=True, figsize=(10, 8), layout="constrained")
r_axis, lt_axis, lat_axis, rhel_axis = axes

r_axis.plot(
    [apoherm_times, periherm_times],
    [apoherm_r, periherm_r],
    color="black",
    lw=0.3,
    alpha=0.3,
)

orbit_times = (apoherm_times, periherm_times)
plot_apoherm_periherm(r_axis, orbit_times, apoherm_r, periherm_r)
plot_apoherm_periherm(lt_axis, orbit_times, apoherm_lt, periherm_lt)
plot_apoherm_periherm(lat_axis, orbit_times, apoherm_lat, periherm_lat)
rhel_axis.plot(apoherm_times, heliocentric_distance, ".", color="black", ms=1.5)

r_axis.set(ylabel=R_LABEL)
lt_axis.set(**LT_SETTINGS)
lat_axis.set(**LAT_SETTINGS)
rhel_axis.set(ylabel=r"$R_{\rm hel}$ [au]")

add_reference_lines(lt_axis, lat_axis)

padding = 0.01 * (periherm_times[-1] - apoherm_times[0])
rhel_axis.set(
    xlabel="Date",
    xlim=(apoherm_times[0] - padding, periherm_times[-1] + padding),
)
rhel_axis.xaxis.set_major_locator(mdates.YearLocator())
rhel_axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
rhel_axis.xaxis.set_minor_locator(mdates.MonthLocator())

finish_figure(axes, legend_columns=2)

plt.show()

# %%
# Four consecutive orbits
# -----------------------
# Over a few orbits the whole trajectory can be drawn, not only apoherm and
# periherm, so each panel follows MESSENGER through every local time it
# passes. Local time is broken
# where it wraps from 24 h back to 0 h. Dotted lines mark each apoherm, where
# one orbit ends and the next begins.
sample_lt_wrapped = sample_lt.copy()
sample_lt_wrapped[1:][np.abs(np.diff(sample_lt)) > 12] = np.nan

window = slice(first_index, first_index + 5)
window_apoherm_periherm_times = (
    apoherm_times[window],
    periherm_times[first_index : first_index + 4],
)

fig, axes = plt.subplots(3, 1, sharex=True, figsize=(10, 6.5), layout="constrained")
r_axis, lt_axis, lat_axis = axes

for ax, values, apoherm, periherm in (
    (r_axis, sample_r, apoherm_r, periherm_r),
    (lt_axis, sample_lt_wrapped, apoherm_lt, periherm_lt),
    (lat_axis, sample_lat, apoherm_lat, periherm_lat),
):
    ax.plot(sample_times, values, color="black", lw=1, alpha=0.3)

    plot_apoherm_periherm(
        ax,
        window_apoherm_periherm_times,
        apoherm[window],
        periherm[first_index : first_index + 4],
        size=6,
    )

for ax in axes:
    for apoherm in apoherm_times[window]:
        ax.axvline(apoherm, color="grey", ls=":", lw=0.8, zorder=0)

for i, periherm in enumerate(periherm_times[first_index : first_index + 4]):
    r_axis.text(
        periherm,
        0.95,
        f"Orbit {FIRST_ORBIT + i}",
        transform=r_axis.get_xaxis_transform(),
        ha="center",
        va="top",
    )

r_axis.set(ylabel=R_LABEL)
lt_axis.set(**LT_SETTINGS)
lat_axis.set(**LAT_SETTINGS)

add_reference_lines(lt_axis, lat_axis)
finish_figure(axes, legend_columns=2, marker_scale=1.5)

locator = mdates.AutoDateLocator()
lat_axis.xaxis.set_major_locator(locator)
lat_axis.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
lat_axis.set_xlim(window_start, window_end)

plt.show()
