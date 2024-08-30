import matplotlib.pyplot as plt
import numpy as np


def Plot_Mercury(
    ax: plt.Axes,
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
