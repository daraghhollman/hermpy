"""
MESSENGER's orbit over the whole mission
========================================

In this example, we summarise MESSENGER's orbital phase in one figure: the
radial distance and local time of each orbit's apoapsis and periapsis, and
the heliocentric distance at the start of each orbit. The line from each
apoapsis to the following periapsis can be coloured by the region MESSENGER
was in.
"""

from bisect import bisect_left, bisect_right
from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import spiceypy as spice
from astropy.table import Table
from astropy.time import Time
from matplotlib.collections import LineCollection

from hermpy.data import CrossingList
from hermpy.net import ClientSPICE
from hermpy.utils import Constants as c
from hermpy.utils import download_files

# %%
# Orbit times
# -----------
# NAIF's orbit number file lists every orbit of the mission. An orbit starts
# at apoapsis, and each line gives that time followed by the time of the
# periapsis within the orbit. The final orbit ends in the impact and has no
# periapsis time, so it is skipped.
ORBNUM_URL = (
    "https://naif.jpl.nasa.gov/pub/naif/pds/data/mess-e_v_h-spice-6-v1.0/"
    "messsp_1000/extras/orbnum/msgr_040803_150430_150430_od431sc_2.orb"
)

[orbnum_path] = download_files([ORBNUM_URL])

apoapsis_times, periapsis_times = [], []

with open(orbnum_path) as orbnum_file:
    for line in orbnum_file:
        fields = line.split()

        if len(fields) != 15 or not fields[0].isdigit():
            continue

        apoapsis_times.append(
            datetime.strptime(" ".join(fields[1:5]), "%Y %b %d %H:%M:%S")
        )
        periapsis_times.append(
            datetime.strptime(" ".join(fields[6:10]), "%Y %b %d %H:%M:%S")
        )

# %%
# Regions
# -------
# Set ``COLOUR_REGIONS`` to ``False`` to leave the lines black.
#
# The solar wind, magnetosheath and magnetosphere come from the bow shock and
# magnetopause crossings of Hollman et al. (2026). Each label names the
# regions either side of a crossing, so the time between two crossings is
# given a region only where both crossings agree on it.
#
# The lobe intervals of Bowers et al. (2024) are not publicly available, and
# are only drawn if a local copy of the list exists.
COLOUR_REGIONS = True

HOLLMAN_URL = "https://zenodo.org/records/21392216/files/hollman_2026_crossing_list.csv"
LOBE_LIST = (
    Path.home() / "Data" / "MESSENGER" / "events" / "MESSENGER_Lobe_Crossings.csv"
)

REGION_COLOURS = {
    "Solar wind": "#F0E442",
    "Magnetosheath": "#009E73",
    "Magnetosphere": "#56B4E9",
    "Lobe": "#CC79A7",
}
REGION_BEFORE = {
    "BS_IN": "Solar wind",
    "BS_OUT": "Magnetosheath",
    "MP_IN": "Magnetosheath",
    "MP_OUT": "Magnetosphere",
}
REGION_AFTER = {
    "BS_IN": "Magnetosheath",
    "BS_OUT": "Solar wind",
    "MP_IN": "Magnetosphere",
    "MP_OUT": "Magnetosheath",
}

[hollman_path] = download_files([HOLLMAN_URL])
crossings = CrossingList.from_csv(hollman_path, time_column="Time").table
crossing_times = crossings["Time"].to_datetime(leap_second_strict="warn")

intervals = []

for i in range(len(crossings) - 1):
    region = REGION_AFTER.get(crossings["Label"][i])

    if region is not None and region == REGION_BEFORE.get(crossings["Label"][i + 1]):
        intervals.append((crossing_times[i], crossing_times[i + 1], region))

if LOBE_LIST.exists():
    lobes = Table.read(LOBE_LIST, format="ascii.csv")
    intervals.extend(
        zip(
            Time(lobes["lobe_start"]).to_datetime(leap_second_strict="warn"),
            Time(lobes["lobe_end"]).to_datetime(leap_second_strict="warn"),
            ["Lobe"] * len(lobes),
        )
    )

# %%
# The lines run from apoapsis to periapsis, so each colour interval is cut when required
region_times = {region: [] for region in REGION_COLOURS}

for start, end, region in intervals:
    first = bisect_right(periapsis_times, start)
    last = bisect_left(apoapsis_times, end)

    for apoapsis, periapsis in zip(
        apoapsis_times[first:last], periapsis_times[first:last]
    ):
        region_times[region].append((max(start, apoapsis), min(end, periapsis)))

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
# 12 h is noon and 18 h is dusk.
def radial_distance_and_local_time(position: np.ndarray):
    x, y, _ = position.T

    radial_distance = np.linalg.norm(position, axis=1) / c.MERCURY_RADIUS.to("km").value
    local_time = (np.degrees(np.arctan2(y, x)) / 15 + 12) % 24

    return radial_distance, local_time


with spice_client.KernelPool():
    apoapsis_ets = spice.datetime2et(apoapsis_times)
    periapsis_ets = spice.datetime2et(periapsis_times)

    apoapsis_position, _ = spice.spkpos(
        "MESSENGER", apoapsis_ets, "MSGR_MSO", "NONE", "MERCURY"
    )
    periapsis_position, _ = spice.spkpos(
        "MESSENGER", periapsis_ets, "MSGR_MSO", "NONE", "MERCURY"
    )
    solar_position, _ = spice.spkpos("MESSENGER", apoapsis_ets, "J2000", "NONE", "SUN")

    # The radial distance at the start and end of each region interval.
    region_r = {}

    for region, times in region_times.items():
        if not times:
            continue

        position, _ = spice.spkpos(
            "MESSENGER",
            spice.datetime2et(np.ravel(times)),
            "MSGR_MSO",
            "NONE",
            "MERCURY",
        )
        region_r[region] = radial_distance_and_local_time(position)[0].reshape(-1, 2)

apoapsis_r, apoapsis_lt = radial_distance_and_local_time(apoapsis_position)
periapsis_r, periapsis_lt = radial_distance_and_local_time(periapsis_position)

AU_IN_KM = 149_597_870.7
heliocentric_distance = np.linalg.norm(solar_position, axis=1) / AU_IN_KM

# %%
# Plotting
# --------
# Every orbit's apoapsis and periapsis is marked. In the first panel a black
# line joins the two, drawn faintly as there are too many orbits to tell the
# lines apart. The regions are drawn over it, so the line stays grey wherever
# the lists give no region.
fig, (r_axis, lt_axis, rhel_axis) = plt.subplots(
    3, 1, sharex=True, figsize=(10, 6.5), layout="constrained"
)

r_axis.plot(
    np.array([apoapsis_times, periapsis_times]),
    np.array([apoapsis_r, periapsis_r]),
    color="black",
    lw=0.3,
    alpha=0.3,
)

if COLOUR_REGIONS:
    for region, r in region_r.items():
        lines = np.stack([mdates.date2num(region_times[region]), r], axis=-1)
        r_axis.add_collection(
            LineCollection(lines, color=REGION_COLOURS[region], lw=0.3, label=region)
        )

for ax, apoapsis, periapsis in (
    (r_axis, apoapsis_r, periapsis_r),
    (lt_axis, apoapsis_lt, periapsis_lt),
):
    ax.plot(apoapsis_times, apoapsis, ".", color="#D55E00", ms=1.5, label="Apoapsis")
    ax.plot(periapsis_times, periapsis, ".", color="#0072B2", ms=1.5, label="Periapsis")

rhel_axis.plot(apoapsis_times, heliocentric_distance, ".", color="black", ms=1.5)

r_axis.set(ylabel=r"R [$R_M$]")
legend = r_axis.legend(
    loc="lower right",
    bbox_to_anchor=(1, 1),
    ncols=6,
    frameon=False,
    markerscale=6,
)
for handle in legend.get_lines():
    handle.set_linewidth(3)
lt_axis.set(ylabel="LT [hours]", ylim=(0, 24), yticks=range(0, 25, 6))
rhel_axis.set(ylabel=r"$R_{\rm hel}$ [au]", xlabel="Date")

for ax, letter in zip((r_axis, lt_axis, rhel_axis), "abc"):
    ax.set_title(f"({letter})", loc="left", fontweight="bold", fontsize="medium")

rhel_axis.margins(x=0.01)
rhel_axis.xaxis.set_major_locator(mdates.YearLocator())
rhel_axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
rhel_axis.xaxis.set_minor_locator(mdates.MonthLocator())

plt.show()
