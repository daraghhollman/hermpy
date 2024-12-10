import datetime as dt

import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import matplotlib.patches
import matplotlib.axes
import matplotlib.figure
import matplotlib.ticker as ticker
import numpy as np

import spiceypy as spice

from hermpy.utils import User, Constants


def Plot_Magnetospheric_Boundaries(
    ax: plt.Axes,
    plane: str = "xy",
    sub_solar_magnetopause: float = 1.45,
    alpha: float = 0.5,
    psi: float = 1.04,
    p: float = 2.75,
    initial_x: float = 0.5,
    add_legend: bool = False,
    zorder: int = 0
) -> None:
    """Add average magnetopause and bow shock locations based on
    Winslow et al. (2013).

    Add the plane projection of the average magnetopause and
    bow shock locations based on Winslow et al. (2013).
    These are plotted in units of Mercury radii.


    Parameters
    ----------
    ax : pyplot.Axes
        The pyplot axis to add the boundaries to.

    plane : str {`"xy"`, `"xz"`, `"yz"`}, optional
        What plane to project the boundaries to. yz is not yet
        implimented.

    add_legend : bool {`True`, `False`}, optional
        Should pyplot legend labels be added.


    Returns
    -------
    None
    """

    # Plotting magnetopause
    phi = np.linspace(0, 2 * np.pi, 1000)
    rho = sub_solar_magnetopause * (2 / (1 + np.cos(phi))) ** alpha

    magnetopause_x_coords = rho * np.cos(phi)
    magnetopause_y_coords = rho * np.sin(phi)

    L = psi * p

    rho = L / (1 + psi * np.cos(phi))

    bowshock_x_coords = initial_x + rho * np.cos(phi)
    bowshock_y_coords = rho * np.sin(phi)

    match plane:
        case "xy":
            bowshock_label = ""
            magnetopause_label = ""

            if add_legend:
                bowshock_label = "Avg. Bowshock (Winslow et al. 2013)"
                magnetopause_label = "Avg. Magnetopause (Winslow et al. 2013)"

            ax.plot(
                magnetopause_x_coords,
                magnetopause_y_coords,
                ls="--",
                lw=1,
                color="black",
                label=magnetopause_label,
                zorder=zorder,
            )
            ax.plot(
                bowshock_x_coords,
                bowshock_y_coords,
                ls="-",
                lw=1,
                color="black",
                label=magnetopause_label,
                zorder=zorder,
            )

        case "xz":

            bowshock_label = ""
            magnetopause_label = ""

            if add_legend:
                bowshock_label = "Avg. Bowshock (Winslow et al. 2013)"
                magnetopause_label = "Avg. Magnetopause (Winslow et al. 2013)"

            ax.plot(
                magnetopause_x_coords,
                magnetopause_y_coords,
                ls="--",
                lw=1,
                color="black",
                label=magnetopause_label,
                zorder=zorder,
            )
            ax.plot(
                bowshock_x_coords,
                bowshock_y_coords,
                ls="-",
                lw=1,
                color="black",
                zorder=zorder,
                label=bowshock_label,
            )

        case "yz":
            pass


def Square_Axes(ax: plt.Axes, distance: float) -> None:
    """Sets axis limits and aspect ratio for square trajectory
    plots.


    Parameters
    ----------
    ax : pyplot.Axes
        The pyplot axis to adjust.

    distance : float
        To what value +/- should the edges extend to.


    Returns
    -------
    None
    """
    ax.set_aspect("equal")
    ax.set_xlim(-distance, distance)
    ax.set_ylim(-distance, distance)

    ax.tick_params(
        which="major",
        direction="in",
        length=20,
        bottom=True,
        top=True,
        left=True,
        right=True,
    )
    ax.tick_params(
        which="minor",
        direction="in",
        length=10,
        bottom=True,
        top=True,
        left=True,
        right=True,
    )

    major_locator = int(distance / 2)
    minor_locator = 0.5

    ax.xaxis.set_major_locator(ticker.MultipleLocator(major_locator))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(minor_locator))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(major_locator))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(minor_locator))


def Add_Labels(ax: plt.Axes, plane: str, frame="MSO") -> None:
    """Adds axes labels corresponding to a particular trajectory
    plane.


    Parameters
    ----------
    ax : pyplot.Axes
        The pyplot axis to add labels to.

    plane : str {`"xy"`, `"xz"`, `"yz"`}
        Which plane is this axis plotting.

    frame : str {`"MSO"`, `"MSM"`, "MSM'"}, optional
        Adjust the coordinate system as written on the labels.


    Returns
    -------
    None
    """

    match plane:
        case "xy":
            ax.set_xlabel(r"X$_{var1}$ [$R_M$]".replace("var1", frame))
            ax.set_ylabel(r"Y$_{var1}$ [$R_M$]".replace("var1", frame))

        case "xz":
            ax.set_xlabel(r"X$_{var1}$ [$R_M$]".replace("var1", frame))
            ax.set_ylabel(r"Z$_{var1}$ [$R_M$]".replace("var1", frame))

        case "yz":
            ax.set_xlabel(r"Y$_{var1}$ [$R_M$]".replace("var1", frame))
            ax.set_ylabel(r"Z$_{var1}$ [$R_M$]".replace("var1", frame))


def Plot_Mercury(
    ax: plt.Axes,
    shaded_hemisphere: str = "none",
    plane: str = "xy",
    frame: str = "MSO",
    border_colour: str = "black"
) -> None:
    """Adds a circle represting Mercury.

    Adds to a pyplot axis a circle (optionally half shaded) to
    represent Mercury. Circle has radius 1 unit and can be offset
    to represent MSM coordinates.


    Parameters
    ----------
    ax : pyplot.Axes
        The pyplot axis to add Mercury to.

    shaded_hemisphere : str {`"none"`, `"top"`, `"bottom"`, `"left"`, `"right"`}, optional
        Which side of Mercury to shade.

    plane : str {`"xy"`, `"xz"`, `"yz"`}, optional
        Which plane is this axis plotting. Needed as frame
        changes only occur for planes containing z.

    frame : str {`"MSO"`, `"MSM"`}, optional
        Shift the coordinate centre.

    border_colour : str {"black"}, optional
        The border colour of the representation of Mercury


    Returns
    -------
    None
    """
    offset: list[float] = [0, 0]

    if frame == "MSM" and (plane == "xz" or plane == "yz"):
        offset[1] -= Constants.DIPOLE_OFFSET_RADII

    angles = np.linspace(0, 2 * np.pi, 1000)
    x_coords = np.cos(angles) + offset[0]
    y_coords = np.sin(angles) + offset[1]

    ax.plot(x_coords, y_coords, color=border_colour)

    match shaded_hemisphere:
        case "left":
            ax.fill_between(
                x_coords, y_coords, where=x_coords < 0, color="black", interpolate=True
            )
            ax.fill_between(
                x_coords, y_coords, where=x_coords > 0, color="white", interpolate=True
            )

        case "right":
            ax.fill_between(
                x_coords, y_coords, where=x_coords > 0, color="black", interpolate=True
            )
            ax.fill_between(
                x_coords, y_coords, where=x_coords < 0, color="white", interpolate=True
            )

        case "top":
            ax.fill_between(
                x_coords, y_coords, where=y_coords > 0, color="black", interpolate=True
            )
            ax.fill_between(
                x_coords, y_coords, where=y_coords < 0, color="white", interpolate=True
            )

        case "bottom":
            ax.fill_between(
                x_coords, y_coords, where=y_coords < 0, color="black", interpolate=True
            )
            ax.fill_between(
                x_coords, y_coords, where=y_coords > 0, color="white", interpolate=True
            )


def Format_Cylindrical_Plot(ax: matplotlib.axes.Axes,
                            size: float = 3,
                            mercury_style: str = "offset",
) -> None:
    """Formats matplotlib axes for use as a cylindrical plot.

    Assumes data is in the MSM' coordinate system.


    Parameters
    ----------

    ax : matplotlib.axes.Axes
        Matplotlib axes to be formatted

    size : float {3}, optional
        Defines the limits of the plot.
            X: (- size, size)
            Y: (0, 2 * size)

    mercury_style : str {offset, centred}, optional
        Should Mercury be plotted with the North-South MSM asymmetry in mind?
        i.e. should two outlines be plotted, offset from each other.
        Or, should Mercury be plotted centred, as one circle with R=1.


    Returns
    -------
    None
    
    """

    # Set aspect
    ax.set_aspect("equal")

    # Set limits
    ax.set_xlim(-size, size)
    ax.set_ylim(0, 2 * size)

    # Set labels
    ax.set_xlabel(r"$\text{X}_{\text{MSM'}} \quad \left[ \text{R}_\text{M} \right]$")
    ax.set_ylabel(r"$\left( \text{Y}_{\text{MSM'}}^2 + \text{Z}_{\text{MSM'}}^2 \right)^{0.5} \quad \left[ \text{R}_\text{M} \right]$")

    ax.tick_params(
        which="major",
        direction="in",
        length=20,
        bottom=True,
        top=True,
        left=True,
        right=True,
    )
    ax.tick_params(
        which="minor",
        direction="in",
        length=10,
        bottom=True,
        top=True,
        left=True,
        right=True,
    )

    minor_locator = 0.5

    ax.xaxis.set_minor_locator(ticker.MultipleLocator(minor_locator))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(minor_locator))

    # Add Mercury
    match mercury_style:

        case "offset":
            Plot_Circle(ax, (0, + Constants.DIPOLE_OFFSET_RADII), 1, ec="k", shade_colour="grey")
            Plot_Circle(ax, (0, - Constants.DIPOLE_OFFSET_RADII), 1, ec="k", shade_colour="grey")

        case "centred":
            Plot_Circle(ax, (0, 0), 1, ec="k", fill=False)


def Plot_Circle(ax: matplotlib.axes.Axes,
                centre: tuple[float, float],
                radius: float = 1,
                shade_half: bool = True,
                shade_colour: str = "grey",
                **kwargs,
) -> None:

    if shade_half:
        w1 = matplotlib.patches.Wedge(centre, radius, 90, 180 + 90, fc=shade_colour, **kwargs)
        w2 = matplotlib.patches.Wedge(centre, radius, 180 + 90, 90, fc="white", **kwargs)

        ax.add_patch(w1)
        ax.add_patch(w2)

        return

    else:
        circle = matplotlib.patches.Circle(centre, radius, **kwargs)
        ax.add_patch(circle)

        return


def Add_Tick_Ephemeris(
    ax: plt.Axes,
    include: set = {"date", "hours", "minutes", "seconds", "range", "latitude", "MLat", "local time"},
) -> None:
    """Adds ephemeris to tick labels

    Formats time series tick labels to include spacecraft
    ephemeris.


    Parameters
    ----------
    ax : pyplot.Axes
        The pyplot axis to affect.

    include : set {"date", "hours", "minutes", "seconds", "range", "latitude", "local time"}
        Which parameters to include as part of the tick labels.

    """

    from hermpy import trajectory

    tick_locations = ax.get_xticks()

    new_tick_labels = []
    with spice.KernelPool(User.METAKERNEL): 
        for loc in tick_locations:
            # Matplotlib stores dates as days since 1970-01-01T00:00:00
            # source: https://matplotlib.org/stable/gallery/text_labels_and_annotations/date.html
            # This can be converted to a datetime object
            date = mpl_dates.num2date(loc)

            tick_format: str = ""

            if "date" in include:
                tick_format += date.strftime("%Y-%m-%d")

            if "hours" in include:
                tick_format += "\n" + date.strftime("%H")
            if "minutes" in include:
                tick_format += date.strftime(":%M")
            if "seconds" in include:
                tick_format += date.strftime(":%S")

            if "range" in include:
                position = trajectory.Get_Position("MESSENGER", date)
                distance = np.sqrt(position[0] ** 2 + position[1] ** 2 + position[2] ** 2)
                # Convert from km to radii
                distance /= Constants.MERCURY_RADIUS_KM

                tick_format += "\n" + f"{distance:.2f}"

            if "longitude" in include:
                position = trajectory.Get_Position("MESSENGER", date)

                longitude = np.arctan2(position[1], position[0]) * 180 / np.pi

                if longitude < 0:
                    longitude += 360

                tick_format += "\n" + f"{longitude:.2f}"

            if "latitude" in include:
                position = trajectory.Get_Position("MESSENGER", date)

                latitude = np.arctan2(
                    position[2], np.sqrt(position[0] ** 2 + position[1] ** 2)
                )

                # convert from radians to degrees
                latitude *= 180 / np.pi

                tick_format += "\n" + f"{latitude:.2f}"

            if "MLat" in include:
                position = trajectory.Get_Position("MESSENGER", date)

                mlat = np.arctan2(
                    position[2] - Constants.DIPOLE_OFFSET_KM, np.sqrt(position[0] ** 2 + position[1] ** 2)
                )

                # convert from radians to degrees
                mlat *= 180 / np.pi

                tick_format += "\n" + f"{mlat:.2f}"

            if "local time" in include:
                position = trajectory.Get_Position("MESSENGER", date)

                longitude = np.arctan2(position[1], position[0]) * 180 / np.pi

                if longitude < 0:
                    longitude += 360

                local_time = ((longitude + 180) * 24 / 360) % 24
                hours = int(local_time)
                minutes = int((local_time * 60) % 60)
                datetime = dt.datetime(year=1, month=1, day=1, hour=hours, minute=minutes)
                tick_format += "\n" + f"{datetime:%H:%M}"

            new_tick_labels.append(tick_format)

        first_tick_format: str = ""
        if "date" in include:
            first_tick_format += "YYYY-MM-DD"

        if "hours" in include:
            first_tick_format += "\nHH"
        if "minutes" in include:
            first_tick_format += ":MM"
        if "seconds" in include:
            first_tick_format += ":SS"

        if "range" in include:
            first_tick_format += "\n" + r"$R_{\text{MSO}}$ [$R_\text{M}$]"

        if "longitude" in include:
            first_tick_format += "\nLon. " + r"[$^\circ$]"
        if "latitude" in include:
            first_tick_format += "\nLat. " + r"[$^\circ$]"
        if "MLat" in include:
            first_tick_format += "\nMLat. " + r"[$^\circ$]"

        if "local time" in include:
            first_tick_format += "\nLT"

        new_tick_labels[0] = first_tick_format

        ax.set_xticks(tick_locations, new_tick_labels)
