import datetime as dt

import matplotlib.pyplot as plt

import numpy as np
import scipy.signal
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


def Get_All_Apoapsis_In_Range(
    start_time: dt.datetime,
    end_time: dt.datetime,
    metakernel: str,
    time_delta: dt.timedelta = dt.timedelta(minutes=1),
    number_of_orbits_to_include: int = 0,
    spacecraft: str = "MESSENGER",
):
    """
    Finds all apoapsis altitudes and times between two times
    """

    spice.furnsh(metakernel)

    current_time = start_time

    altitudes = []
    times = []

    while current_time < end_time:

        # Get current altitude
        et = spice.str2et(current_time.strftime("%Y-%m-%d %H:%M:%S"))
        position, _ = spice.spkpos(spacecraft, et, "IAU_MERCURY", "NONE", "MERCURY")
        current_altitude = np.sqrt(
            position[0] ** 2 + position[1] ** 2 + position[2] ** 2
        )

        altitudes.append(current_altitude)
        times.append(current_time)

        current_time += time_delta

    # Now we find the peaks and their times using scipy.signal
    peak_indices, _ = scipy.signal.find_peaks(altitudes)

    apoapsis_altitudes = np.array(altitudes)[peak_indices]
    apoapsis_times = np.array(times)[peak_indices]

    if number_of_orbits_to_include > 0:

        """
        # if the number of apoapses is greater than the number of orbits
        # we must remove the furthest apoapsis until they are equal
        while len(apoapsis_altitudes) > number_of_orbits_to_include:

            # find the furthest one from the start time
            # it will be at one of the ends
            first_apoapsis_time = apoapsis_times[0]
            last_apoapsis_time = apoapsis_times[-1]

            first_time_difference = start_time - first_apoapsis_time
            last_time_difference = last_apoapsis_time - start_time

            if first_time_difference > last_time_difference:
                # remove first
                apoapsis_times = np.delete(apoapsis_times, 0)
                apoapsis_altitudes = np.delete(apoapsis_altitudes, 0)

            elif last_time_difference > first_time_difference:
                # remove last
                apoapsis_times = np.delete(apoapsis_times, -1)
                apoapsis_altitudes = np.delete(apoapsis_altitudes, -1)

            else:
                raise ValueError("Cannot reduce apoapsis list from 1 orbit. Instead, use trajectory.Get_Nearest_Apoapsis")
        """
        # Remove the first apoapsis, as we always refere to the next apoapsis
        apoapsis_times = np.delete(apoapsis_times, 0)
        apoapsis_altitudes = np.delete(apoapsis_altitudes, 0)


    return apoapsis_altitudes, apoapsis_times 


def Get_Nearest_Apoapsis(
    time: dt.datetime,
    metakernel: str,
    time_delta: dt.timedelta = dt.timedelta(minutes=1),
    time_limit: dt.timedelta = dt.timedelta(hours=12),
    plot: bool = False,
    spacecraft: str = "MESSENGER",
) -> tuple[dt.datetime, float]:
    """
    Finds closest apoapsis to input time and returns apoapsis time
    and altitude
    """
    apoapsis_altitude: float = 0
    apoapsis_time: dt.datetime = time

    spice.furnsh(metakernel)

    # Get all position data within time +- time_delta
    search_start = time - time_limit
    search_end = time + time_limit

    current_time = search_start

    altitudes = []
    times = []

    while current_time < search_end:

        # Get current altitude
        et = spice.str2et(current_time.strftime("%Y-%m-%d %H:%M:%S"))
        position, _ = spice.spkpos(spacecraft, et, "IAU_MERCURY", "NONE", "MERCURY")
        current_altitude = np.sqrt(
            position[0] ** 2 + position[1] ** 2 + position[2] ** 2
        )

        altitudes.append(current_altitude)
        times.append(current_time)

        current_time += time_delta

    # Now we find the peaks and their times using scipy.signal
    peak_indices, _ = scipy.signal.find_peaks(altitudes)

    # Check for the closest one
    time_distances = []
    for i in peak_indices:
        peak_time = times[i]

        time_distance = abs(time - peak_time)
        time_distances.append(time_distance)

    closest_apoapsis_index = peak_indices[np.argmin(time_distances)]

    print(altitudes[closest_apoapsis_index])
    print(times[closest_apoapsis_index])

    if plot:
        plt.plot(times, altitudes)
        plt.scatter(np.array(times)[peak_indices], np.array(altitudes)[peak_indices])
        plt.axvline(time)
        plt.show()

    apoapsis_time = times[closest_apoapsis_index]
    apoapsis_altitude = altitudes[closest_apoapsis_index]

    return apoapsis_time, apoapsis_altitude
