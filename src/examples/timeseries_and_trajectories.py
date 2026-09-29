"""
Timeseries and trajectories
===========================

MESSENGER MAG data are only half the story: where the spacecraft was when it
made a measurement matters as much as the measurement itself. Here we download
a single orbit and draw both together in one figure. The upper two rows show
the field magnitude and its components against time, and the lower row shows
the trajectory they were measured along, projected onto the X-Y, X-Z, and
X-rho planes.
"""

import datetime as dt

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
from matplotlib.patches import Circle, Polygon
from matplotlib import patheffects
from matplotlib.ticker import MaxNLocator, MultipleLocator
from sunpy.time import TimeRange

from hermpy.data import (
    add_field_magnitude,
    parse_messenger_mag,
    rotate_to_aberrated_coordinates,
)
from hermpy.net import ClientMESSENGER, ClientSPICE
from hermpy.plotting import plot_magnetospheric_boundaries
from hermpy.utils import Constants as c

# AGU/JGR figure guidelines: sans-serif font, >=8 pt at final print size, and
# >=0.5 pt line weight (https://www.agu.org/publications/authors/journals/figures).
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "mathtext.fontset": "dejavusans",
        "font.size": 10,
        "axes.labelsize": 10,
        "axes.titlesize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
    }
)

# %%
# Downloading the data
# --------------------
# We use ``hermpy.net.ClientMESSENGER`` to fetch one orbit of 60 second
# averaged MAG data. See `here <download_data.html>`_ for more details.
time_range = TimeRange("2012-04-01 05:00", dt.timedelta(hours=8))

downloader = ClientMESSENGER()
downloader.query(time_range, "MAG 60s")
files = downloader.fetch()

# %%
# Preparing the data
# ------------------
# The MAG files carry the ephemeris alongside the field, so a single parse
# gives us everything the figure needs. We add the field magnitude, shift the
# ephemeris into MSM by the dipole offset, and rotate both the position and
# the field into the aberrated frame. See `here
# <plot_one_orbit_of_messenger_mag.html>`_ for these steps in more detail.
data = parse_messenger_mag(files, time_range)
data = add_field_magnitude(data)

data["X MSM"] = data["X MSO"]
data["Y MSM"] = data["Y MSO"]
data["Z MSM"] = data["Z MSO"] - c.DIPOLE_OFFSET

spice_client = ClientSPICE()
with spice_client.KernelPool():
    data = rotate_to_aberrated_coordinates(data)

# %%
# Positions are most readable in Mercury radii. The third projection uses the
# cylindrical radius, :math:`\rho = \sqrt{Y'^2 + Z'^2}`, which folds the two
# off-Sun axes into one and so shows the whole orbit against the boundaries
# regardless of how it is oriented about the X axis.
times = data["UTC"].to_datetime(leap_second_strict="warn")

x = data["X MSM'"].to("Mercury Radii").value
y = data["Y MSM'"].to("Mercury Radii").value
z = data["Z MSM'"].to("Mercury Radii").value
rho = np.sqrt(y**2 + z**2)

# %%
# Laying out the figure
# ---------------------
# The two timeseries rows share a time axis, while the three trajectory panels
# each need a square aspect and their own limits. We therefore split the
# figure into two blocks: an upper block holding the timeseries rows, and a
# lower block holding the trajectory row.
# A fixed aspect leaves the trajectory panels shorter than the cells they sit
# in, and the slack shows up as whitespace above the figure. ``compressed``
# layout takes that slack out instead of centring the panels in it.
figure = plt.figure(
    figsize=(7.5, 4.5)
)  # AGU full (2-column) page width: 19 cm / 7.5 in
figure.set_layout_engine("compressed", wspace=0.06, hspace=0.08)
upper_block, lower_block = figure.add_gridspec(2, 1, height_ratios=[2, 1.6])

trajectory_axes = upper_block.subgridspec(1, 3).subplots()
magnitude_axis, components_axis = lower_block.subgridspec(2, 1).subplots(sharex=True)

# The figure is empty until the blocks below fill it, so hold off the capture.
# sphinx_gallery_defer_figures

# %%
# The timeseries rows
# -------------------
# Colours are from a 7-colour palette by Wong (2023) [1]_. A ``ConciseDateFormatter``
# keeps the time ticks readable without spelling out the date at every one.
magnitude_axis.plot(times, data["|B|"].value, color="black", lw=1)
magnitude_axis.set_ylabel(r"|B| (nT)")
magnitude_axis.yaxis.set_major_locator(MaxNLocator(nbins=5, min_n_ticks=4))
magnitude_axis.text(
    0.02,
    0.9,
    "(d)",
    transform=magnitude_axis.transAxes,
    ha="left",
    va="top",
    fontweight="bold",
)

components = ["Bx'", "By'", "Bz'"]
labels = [r"B$_{x'}$", r"B$_{y'}$", r"B$_{z'}$"]
colours = ["#D55E00", "#009E73", "#0072B2"]

for component, label, colour in zip(components, labels, colours):
    components_axis.plot(
        times,
        data[component].value,
        color=colour,
        label=label,
        lw=1.4,
        path_effects=[  # Add a black outline to the line
            patheffects.Stroke(linewidth=1.7, foreground="black"),
            patheffects.Normal(),
        ],
    )

components_axis.axhline(0, color="grey", ls="dotted", lw=0.6, zorder=0)
components_axis.set_ylabel(r"B (nT)")
components_axis.yaxis.set_major_locator(MaxNLocator(nbins=5, min_n_ticks=4))
components_axis.legend(ncols=3, loc="upper right", frameon=False)
components_axis.text(
    0.02,
    0.9,
    "(e)",
    transform=components_axis.transAxes,
    ha="left",
    va="top",
    fontweight="bold",
)

locator = AutoDateLocator()
components_axis.xaxis.set_major_locator(locator)
components_axis.xaxis.set_major_formatter(ConciseDateFormatter(locator))

magnitude_axis.margins(x=0)
components_axis.margins(x=0)
# set the ylimits to be symmetric about zero, with a 10% margin
ylimits = components_axis.get_ylim()
components_axis.set_ylim(
    -1.1 * max(abs(ylimits[0]), abs(ylimits[1])),
    1.1 * max(abs(ylimits[0]), abs(ylimits[1])),
)

# sphinx_gallery_defer_figures

# %%
# The trajectory row
# ------------------
# Each panel gets Mercury, the average boundaries of Winslow et al. (2013) [2]_,
# and the track itself, with a marker at the start of the orbit.
#
# ``plot_magnetospheric_boundaries`` has no ``x-rho`` plane of its own, but the
# models are figures of revolution about the X axis, so the ``xy`` curves are
# the same ones we want; restricting the panel to positive :math:`\rho` leaves
# only the half we can reach.
dipole_offset = c.DIPOLE_OFFSET_RADII.value
extent = float(np.ceil(np.max([np.abs(x), np.abs(y), np.abs(z)])) + 0.5)

planet_style = {"facecolor": "lightgrey", "edgecolor": "black", "lw": 0.6, "zorder": 1}


def mercury_in_cylindrical_projection(offset: float, resolution: int = 181):
    """
    Mercury's outline in the X-rho plane, drawn as two half circles.

    Rho is measured from the MSM origin, which sits on the dipole, ``offset``
    north of the planet centre, and folding the hemispheres onto rho >= 0
    superposes them. The limb therefore splits in two: the southern half of
    the planet becomes a unit semicircle centred at ``+offset``, and the
    northern half one centred at ``-offset``.
    """

    limb_x = np.cos(np.linspace(0, np.pi, resolution))
    limb = np.sqrt(1 - limb_x**2)

    # At each X the planet's cross section is a disc of radius sqrt(1 - X^2),
    # centred `offset` away from the origin of rho. It therefore covers every
    # rho out to the southern limb, and the body is filled to there.
    southern = np.column_stack([limb_x, limb + offset])
    body = np.vstack([southern, [[limb_x[-1], 0], [limb_x[0], 0]]])

    # The northern limb runs below it, reaching rho = 0 at the poles.
    northern = np.column_stack([limb_x, limb - offset])

    return [
        Polygon(body, **planet_style),
        Polygon(
            northern[northern[:, 1] >= 0],
            closed=False,
            fill=False,
            edgecolor=planet_style["edgecolor"],
            lw=planet_style["lw"],
            zorder=planet_style["zorder"],
        ),
    ]


panels = [
    (
        "xy",
        y,
        r"Y$_{\rm MSM'}$ (R$_M$)",
        [Circle((0, 0), 1, **planet_style)],
        (-extent, extent),
    ),
    (
        "xz",
        z,
        r"Z$_{\rm MSM'}$ (R$_M$)",
        [Circle((0, -dipole_offset), 1, **planet_style)],
        (-extent, extent),
    ),
    (
        "xy",
        rho,
        r"$\rho_{\rm MSM'}$ (R$_M$)",
        mercury_in_cylindrical_projection(dipole_offset),
        (0, 2 * extent),
    ),
]

panel_letters = "abc"

for index, (axis, panel) in enumerate(zip(trajectory_axes, panels)):
    plane, vertical, vertical_label, planet, ylim = panel

    for artist in planet:
        axis.add_artist(artist)

    plot_magnetospheric_boundaries(axis, plane, add_legend=(index == 0))

    axis.plot(x, vertical, color="black", lw=1, zorder=2)
    axis.plot(
        x[0],
        vertical[0],
        "o",
        color="#E69F00",
        markeredgecolor="black",
        markeredgewidth=0.6,
        zorder=3,
    )

    # X is drawn sunward-right, as is conventional.
    axis.set(
        xlim=(-extent, extent),
        ylim=ylim,
        aspect="equal",
        xlabel=r"X$_{\rm MSM'}$ (R$_M$)",
        ylabel=vertical_label,
    )
    axis.text(
        0.05,
        0.94,
        f"({panel_letters[index]})",
        transform=axis.transAxes,
        ha="left",
        va="top",
        fontweight="bold",
    )
    # Matching tick spacing on both axes keeps the square panels from
    # showing denser, decimal ticks on one side and round ones on the other.
    axis.xaxis.set_major_locator(MultipleLocator(5))
    axis.yaxis.set_major_locator(MultipleLocator(5))

# sphinx_gallery_defer_figures

# %%
# Finally, the boundary labels are collected into a single legend beneath the
# trajectory row rather than crowding the panel they were requested on.
handles, boundary_labels = trajectory_axes[0].get_legend_handles_labels()
figure.legend(
    handles,
    boundary_labels,
    loc="outside lower center",
    ncols=2,
    fontsize=9,
    frameon=False,
)

plt.show()

# %%
# References
# ----------
#
# .. [1] Wong (2023),
#        *Points of view: Colorblindness*,
#        Nature Methods,
#        https://doi.org/10.1038/nmeth.1618
#
# .. [2] Winslow et al. (2013),
#        *Mercury's magnetopause and bow shock from MESSENGER Magnetometer
#        observations*,
#        Journal of Geophysical Research: Space Physics,
#        https://doi.org/10.1002/jgra.50237
