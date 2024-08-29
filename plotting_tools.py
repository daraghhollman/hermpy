import matplotlib.pyplot as plt
import numpy as np
import spiceypy as spice


def main():
    """A simple example"""

    # metakernel created using autometa
    metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"

    # we are going to get positions between these two dates
    dates = ["2012-06-10", "2012-06-20"]

    positions = Get_Trajectory("Messenger", dates, metakernel)

    positions /= 2439.7 # convert from km to radii

    fig, ax = plt.subplots()

    ax.plot(positions[:, 0], positions[:, 1])

    Plot_Mercury(ax, shaded_hemisphere="left")

    ax.set_aspect("equal")

    plt.show()


def Get_Trajectory(spacecraft: str, dates: list[str], metakernel: str, steps=4000):
    """
    Plots a given spacecraft's trajectory between two dates. A SPICE metakernel with the required ephemerids must be provided
    Returns: spacecraft positions in km
    """

    spice.furnsh(metakernel)

    et_one = spice.str2et(dates[0])
    et_two = spice.str2et(dates[1])

    times = [x * (et_two - et_one) / steps + et_one for x in range(steps)]

    positions, _ = spice.spkpos(spacecraft, times, "J2000", "NONE", "MERCURY")

    return positions


def Plot_Mercury(
    ax,
    shaded_hemisphere: str = "none",
    offset: tuple[float, float] = (0, 0),
) -> None:
    """
    Adds mercury circle at 0, 0 on matplotlib axis 'ax'
    In units of Mercury radii

    shade_hemisphere: ['left', 'right', 'top', or 'bottom']
                      shades half the circle darker
    """

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


if __name__ == "__main__":
    main()
