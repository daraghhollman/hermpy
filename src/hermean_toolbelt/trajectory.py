import datetime as dt

import numpy as np
import spiceypy as spice


def Get_Position(spacecraft: str, date: dt.datetime, metakernel: str) -> list[float]:
    """
    Returns spacecraft position
    """
    spice.furnsh(metakernel)

    et = spice.str2et(date.strftime("%Y-%m-%d %H:%M:%S"))

    position, _ = spice.spkpos(spacecraft, et, "IAU_MERCURY", "NONE", "MERCURY")

    return position


def Get_Trajectory(
    spacecraft: str, dates: list[str], metakernel: str, steps=4000, frame="MSO"
):
    """
    Plots a given spacecraft's trajectory between two dates. A SPICE metakernel with the required ephemerids must be provided
    Returns: spacecraft positions in km
    """

    spice.furnsh(metakernel)

    et_one = spice.str2et(dates[0])
    et_two = spice.str2et(dates[1])

    times = [x * (et_two - et_one) / steps + et_one for x in range(steps)]

    positions, _ = spice.spkpos(spacecraft, times, "IAU_MERCURY", "NONE", "MERCURY")

    match frame:
        case "MSO":
            return positions

        case "MSM":
            positions[:, 2] += 479
            return positions

    return positions


def Get_Range_From_Date(
    spacecraft: str, dates: list[dt.datetime] | dt.datetime, metakernel: str
):
    """
    For a date, or range of dates, return a spacecraft's distance from Mercury
    """

    if type(dates) == dt.datetime:
        dates = [dates]

    spice.furnsh(metakernel)

    distances = []

    for date in dates:
        et = spice.str2et(date.strftime("%Y-%m-%d %H:%M:%S"))

        position, _ = spice.spkpos(spacecraft, et, "IAU_MERCURY", "NONE", "MERCURY")

        distance = np.sqrt(position[0] ** 2 + position[1] ** 2 + position[2] ** 2)
        distances.append(distance)

    if len(distances) == 1:
        return distances[0]

    return distances
