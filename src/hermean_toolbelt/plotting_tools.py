import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator


def PlotMagnetosphericBoundaries(
    ax: plt.Axes,
    plane: str = "xy",
    sub_solar_magnetopause: float = 1.45,
    alpha: float = 0.5,
    psi: float = 1.04,
    p: float = 2.75,
    initial_x: float = 0.5,
) -> None:
    """
    Add nominal magnetopause and bow shock locations based on
    Winslow et al. (2013)
    """

    # Plotting magnetopause

    # need to give these better names
    # discuss with Charlie, and look into Winslow paper
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
            ax.plot(
                magnetopause_x_coords,
                magnetopause_y_coords,
                ls="--",
                lw=3,
                color="black",
            )
            ax.plot(
                bowshock_x_coords,
                bowshock_y_coords,
                ls="-",
                lw=3,
                color="black",
            )

        case "xz":
            ax.plot(
                magnetopause_x_coords,
                magnetopause_y_coords,
                ls="--",
                lw=3,
                color="black",
            )
            ax.plot(
                bowshock_x_coords,
                bowshock_y_coords,
                ls="-",
                lw=3,
                color="black",
            )

        case "yz":
            pass


def SquareAxes(ax: plt.Axes, distance: float) -> None:
    """
    Sets limits and aspect ratio of ax
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

    ax.xaxis.set_major_locator(MultipleLocator(major_locator))
    ax.xaxis.set_minor_locator(MultipleLocator(minor_locator))
    ax.yaxis.set_major_locator(MultipleLocator(major_locator))
    ax.yaxis.set_minor_locator(MultipleLocator(minor_locator))


def AddLabels(ax: plt.Axes, plane: str, frame="MSO") -> None:
    """
    Adds axes labels corresponding to a particular viewplane
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
    offset: list[float] = [0, 0],
) -> None:
    """
    Adds mercury circle at 0, 0 on matplotlib axis 'ax'
    In units of Mercury radii

    shade_hemisphere: ['left', 'right', 'top', or 'bottom']
                      shades half the circle darker
    """

    if frame == "MSM" and (plane == "xz" or plane == "yz"):
        offset[1] += 479 / 2439.7

    angles = np.linspace(0, 2 * np.pi, 1000)
    x_coords = np.cos(angles) + offset[0]
    y_coords = np.sin(angles) + offset[1]

    ax.plot(x_coords, y_coords, color="black")

    match shaded_hemisphere:
        case "left":
            ax.fill_between(
                x_coords, y_coords, where=x_coords < 0, color="black", interpolate=True
            )

        case "right":
            ax.fill_between(
                x_coords, y_coords, where=x_coords > 0, color="black", interpolate=True
            )

        case "top":
            ax.fill_between(
                x_coords, y_coords, where=y_coords > 0, color="black", interpolate=True
            )

        case "bottom":
            ax.fill_between(
                x_coords, y_coords, where=y_coords < 0, color="black", interpolate=True
            )


def Add_Tick_Ephemeris(
    ax: plt.Axes,
    metakernel: str,
    include: set = {"date", "hours", "minutes", "seconds", "range"},
):

    from hermean_toolbelt import trajectory

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
            position = trajectory.Get_Position("MESSENGER", date, metakernel)
            distance = np.sqrt(position[0] ** 2 + position[1] ** 2 + position[2] ** 2)
            # Convert from km to radii
            distance /= 2439.7

            tick_format += "\n" + f"{distance:.2f}"

        if "longitude" in include:
            position = trajectory.Get_Position("MESSENGER", date, metakernel)

            longitude = np.arctan2(position[1], position[0]) * 180 / np.pi

            if longitude < 0:
                longitude += 360

            tick_format += "\n" + f"{longitude:.2f}"

        if "latitude" in include:
            position = trajectory.Get_Position("MESSENGER", date, metakernel)

            latitude = np.arctan2(
                position[2], np.sqrt(position[0] ** 2 + position[1] ** 2)
            )

            # convert from radians to degrees
            latitude *= 180 / np.pi

            tick_format += "\n" + f"{latitude:.2f}"

        if "local time" in include:
            position = trajectory.Get_Position("MESSENGER", date, metakernel)

            longitude = np.arctan2(position[1], position[0]) * 180 / np.pi

            if longitude < 0:
                longitude += 360
            
            local_time = ((longitude + 180) * 24 / 360) % 24
            tick_format += "\n" + f"{local_time:.0f}"

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
        first_tick_format += "\n"+r"$R_{\text{MSO}}$ [$R_\text{M}$]"

    if "longitude" in include:
        first_tick_format += "\nLon. " + r"[$^\circ$]"
    if "latitude" in include:
        first_tick_format += "\nLat. " + r"[$^\circ$]"

    if "local time" in include:
        first_tick_format += "\nLT"

    new_tick_labels[0] = first_tick_format

    ax.set_xticklabels(new_tick_labels)
