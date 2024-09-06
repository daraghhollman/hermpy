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


def Get_Nearest_Apoapsis(
    time: dt.datetime,
    metakernel: str,
    time_delta: dt.timedelta = dt.timedelta(minutes=1),
    time_limit: dt.timedelta = dt.timedelta(hours=12),
    spacecraft: str = "MESSENGER",
) -> tuple[dt.datetime, float]:
    """
    Finds closest apoapsis to input time and returns apoapsis time
    and altitude
    """
    apoapsis_altitude: float = 0
    apoapsis_time: dt.datetime = time

    spice.furnsh(metakernel)

    # Search forward in time
    current_time = time
    end_time = time + time_limit
    while current_time < end_time:

        # Get current altitude
        et = spice.str2et(current_time.strftime("%Y-%m-%d %H:%M:%S"))
        position, _ = spice.spkpos(spacecraft, et, "IAU_MERCURY", "NONE", "MERCURY")
        altitude = np.sqrt(position[0] ** 2 + position[1] ** 2 + position[2] ** 2)

        if altitude > apoapsis_altitude:
            apoapsis_altitude = altitude
            apoapsis_time = current_time

        current_time += time_delta


    # Search backward in time
    current_time = time
    end_time = time - time_limit
    while current_time > end_time:

        # Get current altitude
        et = spice.str2et(current_time.strftime("%Y-%m-%d %H:%M:%S"))
        position, _ = spice.spkpos(spacecraft, et, "IAU_MERCURY", "NONE", "MERCURY")
        altitude = np.sqrt(position[0] ** 2 + position[1] ** 2 + position[2] ** 2)

        if altitude > apoapsis_altitude:
            apoapsis_altitude = altitude
            apoapsis_time = current_time

        current_time -= time_delta

    return apoapsis_time, apoapsis_altitude
