import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np


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
            ax.set_xlabel(f"X {frame} [$R_M$]")
            ax.set_ylabel(f"Y {frame} [$R_M$]")

        case "xz":
            ax.set_xlabel(f"X {frame} [$R_M$]")
            ax.set_ylabel(f"Z {frame} [$R_M$]")

        case "yz":
            ax.set_xlabel(f"Y {frame} [$R_M$]")
            ax.set_ylabel(f"Z {frame} [$R_M$]")



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


if __name__ == "__main__":
    main()
