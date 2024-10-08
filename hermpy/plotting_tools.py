import datetime as dt

import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


def Plot_Magnetospheric_Boundaries(
    ax: plt.Axes,
    plane: str = "xy",
    frame="MSO",
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
    phi = np.linspace(0, 2 * np.pi, 100)
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


def Add_Labels(ax: plt.Axes, plane: str, frame="MSO", aberrate=False) -> None:
    """Adds axes labels corresponding to a particular trajectory
    plane.


    Parameters
    ----------
    ax : pyplot.Axes
        The pyplot axis to add labels to.

    plane : str {`"xy"`, `"xz"`, `"yz"`}
        Which plane is this axis plotting.

    frame : str {`"MSO"`, `"MSM"`}, optional
        Adjust the coordinate system as written on the labels.

    aberrate : bool {`False`, `True`}, optional
        Prime the coordinate labels. e.g. X -> X'


    Returns
    -------
    None
    """

    match plane:
        case "xy":
            if aberrate:
                ax.set_xlabel(r"X'$_{var1}$ [$R_M$]".replace("var1", frame))
                ax.set_ylabel(r"Y'$_{var1}$ [$R_M$]".replace("var1", frame))
            else:
                ax.set_xlabel(r"X$_{var1}$ [$R_M$]".replace("var1", frame))
                ax.set_ylabel(r"Y$_{var1}$ [$R_M$]".replace("var1", frame))

        case "xz":
            if aberrate:
                ax.set_xlabel(r"X'$_{var1}$ [$R_M$]".replace("var1", frame))
                ax.set_ylabel(r"Z'$_{var1}$ [$R_M$]".replace("var1", frame))
            else:
                ax.set_xlabel(r"X$_{var1}$ [$R_M$]".replace("var1", frame))
                ax.set_ylabel(r"Z$_{var1}$ [$R_M$]".replace("var1", frame))

        case "yz":
            if aberrate:
                ax.set_xlabel(r"Y'$_{var1}$ [$R_M$]".replace("var1", frame))
                ax.set_ylabel(r"Z'$_{var1}$ [$R_M$]".replace("var1", frame))
            else:
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
        offset[1] -= 479 / 2439.7

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


def Add_Tick_Ephemeris(
    ax: plt.Axes,
    include: set = {"date", "hours", "minutes", "seconds", "range", "latitude", "local time"},
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
            distance /= 2439.7

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

    if "local time" in include:
        first_tick_format += "\nLT"

    new_tick_labels[0] = first_tick_format

    ax.set_xticklabels(new_tick_labels)
