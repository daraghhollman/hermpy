import datetime as dt

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal
import scipy.spatial
import spiceypy as spice
from tqdm import tqdm

import hermpy.trajectory as traj

from .utils import Constants, User


def Get_Heliocentric_Distance(date: dt.datetime | dt.date) -> float:
    """Gets the distance from Mercury to the Sun, assumes a SPICE metakernel is loaded.


    Parameters
    ----------
    date : dt.datetime
        The date to query at.


    Returns
    -------
    distance : float
        The distance from Mercury to the sun at time `date` in km
    """

    with spice.KernelPool(User.METAKERNEL):
        et = spice.str2et(date.strftime("%Y-%m-%d %H:%M:%S"))
        position, _ = spice.spkpos("MERCURY", et, "J2000", "NONE", "SUN")

        distance = np.sqrt(position[0] ** 2 + position[1] ** 2 + position[2] ** 2)

        return distance


def Longitude(position: list[float]) -> float:

    longitude = np.arctan2(position[1], position[0])
    longitude = Constants.RADIANS_TO_DEGREES(longitude)

    if longitude < 0:
        longitude += 360

    return longitude


def Local_Time(position: list[float]) -> float:

    local_time = ((Longitude(position) + 180) * 24 / 360) % 24

    return local_time


def Latitude(position: list[float]) -> float:

    latitude = np.arctan2(position[2], np.sqrt(position[0] ** 2 + position[1] ** 2))
    latitude = Constants.RADIANS_TO_DEGREES(latitude)

    return latitude


def Magnetic_Latitude(position: list[float]) -> float:

    magnetic_latitude = np.arctan2(position[2] - Constants.DIPOLE_OFFSET_RADII,
                                   np.sqrt(position[0] ** 2 + position[1] ** 2))
    magnetic_latitude = Constants.RADIANS_TO_DEGREES(magnetic_latitude)

    return magnetic_latitude


def Get_Position(spacecraft: str, date: dt.datetime, frame: str = "MSO", aberrate=False):
    """Returns spacecraft position at a given time

    Uses SPICE to find the position of an input spacecraft
    at a given time. Assumes the needed SPICE kernels are already loaded.


    Parameters
    ----------
    spacecraft : str
        The name of the spacecraft to query. i.e. 'MESSENGER'.

    date : datetime.datetime
        The date and time to query at.

    frame : str {"MSO", "MSM"}, optional
        The SPICE frame to load


    Returns
    -------
    position : list[float]
        The position in the MSO / MSM coordinate frame. In km.
    """

    with spice.KernelPool(User.METAKERNEL):
        et = spice.str2et(date.strftime("%Y-%m-%d %H:%M:%S"))

        # There are data gaps in the kernels?
        # We need to test for this
        try:
            position, _ = spice.spkpos(spacecraft, et, "BC_MSO", "NONE", "MERCURY")

            match frame:
                case "MSO":
                    pass

                case "MSM":
                    position[2] -= Constants.DIPOLE_OFFSET_KM

            if aberrate:
                position = Aberrate_Position(position, date.date())

            return position

        except:
            raise RuntimeError(f"Unable to load ephemeris for datetime: {date}")


def Get_Trajectory(
    spacecraft: str,
    dates: list[dt.datetime],
    steps: int = 100,
    frame: str = "MSO",
    aberrate: bool = False,
    verbose: bool = False,
):
    """Finds a given spacecraft's trajectory between two dates.

    Uses SPICE to find the position of an input spacecraft
    for a number of `steps` between two dates.
    Assumes the needed SPICE kernels are already loaded.


    Parameters
    ----------
    spacecraft : str
        The name of the spacecraft to query. i.e. 'MESSENGER'.

    dates : list[datetime.datetime]
        The start and end date and time to query at.

    steps : int {100}, optional
        The number of points to sample beween the two times.

    frame : str {MSO, MSM}, optional
        What frame to return the points in.

    aberrate : bool {False}
        Set True to return the positions in the aberrated
        coordinate system.
        Aberration angle is determined using an average
        solar wind velocity if 400 km/s, with Mercury's
        velocity sampled daily.


    Returns
    -------
    positions : numpy.array
        The position of the given spacecraft for each of the
        `steps` between `dates[0]` and `dates[1]`.
        Formatted as follows:
        [[x, y, z],
         [x, y, z],
         ...
        ]
    """

    with spice.KernelPool(User.METAKERNEL):

        dates = [dates[0] + (t * (dates[1] - dates[0]) / steps) for t in range(steps)]
        spice_times = spice.str2et([date.strftime("%Y-%m-%d %H:%M:%S") for date in dates])

        positions, _ = spice.spkpos(spacecraft, spice_times, "BC_MSO", "NONE", "MERCURY")

        if aberrate:
            # Precompute aberration angles
            aberration_angles = np.array([Get_Aberration_Angle(date.date()) for date in dates])

            # Create rotation matrices
            cos_angles = np.cos(aberration_angles)
            sin_angles = np.sin(aberration_angles)

            rotation_matrices = np.array([
                [[cos, -sin, 0],
                 [sin,  cos, 0],
                 [0,      0, 1]]
                for cos, sin in zip(cos_angles, sin_angles)
            ])


            positions = np.einsum('ijk,ik->ij', rotation_matrices, positions)

        match frame:
            case "MSO":
                return positions

            case "MSM":
                positions[:, 2] -= Constants.DIPOLE_OFFSET_KM
                return positions

        return positions


def Aberrate_Position(position: list[float], date: dt.datetime | dt.date, verbose=False):
    """Rotate the spacecraft coordinates into the aberrated coordinate system.


    For a given position and date, rotates the spacecraft coordinates into the
    aberrated system. Assumes a metakernel is already loaded.
    It is easier to use `Get_Trajectory()` with `aberrate = True` instead of
    this function.

    Parameters
    ----------
    position : list[float]
        A list of coordinates in a non-aberrated frame, [x, y, z].

    spice_date : float
        Epoch of transformation in seconds past J2000 TDB.


    Returns
    -------
    rotated_position : list[float]
        The new position, rotated into the aberrated frame.
    """

    with spice.KernelPool(User.METAKERNEL):

        aberration_angle = Get_Aberration_Angle(date)

        rotation_matrix = np.array(
            [
                [np.cos(aberration_angle), -np.sin(aberration_angle), 0],
                [np.sin(aberration_angle), np.cos(aberration_angle), 0],
                [0, 0, 1],
            ]
        )

        rotated_position = np.matmul(rotation_matrix, position)

        return rotated_position


def Get_Aberration_Angle(date: dt.datetime | dt.date) -> float:
    """For a given date, find the solar wind aberration angle.

    Uses a daily average

    Parameters
    ----------
    date : dt.datetime | str | float
        The datetime to determine the aberration angle


    Returns
    -------
    angle : float
        Aberration Angle

    """

    if type(date) == dt.datetime:
        mercury_distance = Get_Heliocentric_Distance(date.date()) * 1000 # convert to meters

    else:
        mercury_distance = Get_Heliocentric_Distance(date) * 1000

    # determine mercury velocity
    a = Constants.MERCURY_SEMI_MAJOR_AXIS
    M = Constants.SOLAR_MASS
    G = Constants.G

    orbital_velocity = np.sqrt(G * M * ((2 / mercury_distance) - (1 / a)))

    # Aberration angle is related to the orbital velocity and the solar wind speed
    # Solar wind speed is assumed to be 400 km/s
    # Angle is minus as y in the coordinate system points away from the orbital velocity
    aberration_angle = np.arctan(
        orbital_velocity / Constants.SOLAR_WIND_SPEED_AVG
    )

    return aberration_angle

def Get_Range_From_Date(
    spacecraft: str, dates: list[dt.datetime] | dt.datetime
) -> list[float]:
    """For a date, or range of dates, return a spacecraft's distance from Mercury

    Finds the distance of a spacecraft from Mercury at a single, or multiple
    datetimes. Assumes the relevant SPICE kernels are loaded.


    Parameters
    ----------
    spacecraft : str
        The name of the spacecraft to query. i.e. 'MESSENGER'.

    dates : list[datetime.datetime] | datetime.datetime
        The date or list of dates to query.


    Returns
    -------
    distances : list[float]
        The spacecraft's distance from Mercury at each time specified.
    """

    with spice.KernelPool(User.METAKERNEL):
        if isinstance(dates, dt.datetime):
            dates = [dates]

        distances = []

        for date in dates:
            et = spice.str2et(date.strftime("%Y-%m-%d %H:%M:%S"))

            position, _ = spice.spkpos(spacecraft, et, "BC_MSO", "NONE", "MERCURY")

            distance = np.sqrt(position[0] ** 2 + position[1] ** 2 + position[2] ** 2)
            distances.append(distance)

        if len(distances) == 1:
            return distances[0]

        return distances


def Get_All_Apoapsis_In_Range(
    start_time: dt.datetime,
    end_time: dt.datetime,
    time_delta: dt.timedelta = dt.timedelta(minutes=1),
    number_of_orbits_to_include: int = 0,
    spacecraft: str = "MESSENGER",
    plot: bool = False,
):
    """Finds all apoapsis altitudes and times between two given dates.

    Finds all apoapsis times and their altitudes between `start_time`
    and `end_time`. Assumes the relevant SPICE kernels are already
    loaded.


    Parameters
    ----------
    start_time : datetime.datetime
        The start date and time of the search.

    end_time : datetime.datetime
        The end date and time of the search.

    time_delta : datetime.timedelta, {datetime.timedelta(minutes=1)}, optional
        The time resolution of the search. Default 1 minute.

    number_of_orbits_to_include : int, {0}, optional
        If set, reduces the number of apoapses in the data until it
        reaches this number. Disabled if left as 0.

    spacecraft : str, {"MESSENGER"}, optional
        Which spacecraft to query.

    plot : bool, {False}, optional
        Displays a plot of the trajectory for debugging purposes.


    Returns
    -------
    apoapsis_altitudes : numpy.array[float]
        The altitude of each apoapsis found.

    apoapsis_times : numpy.array[datetime.datetime]
        The dates and times of each apoapsis found.
    """
    with spice.KernelPool(User.METAKERNEL):
        current_time = start_time

        altitudes = []
        times = []

        while current_time < end_time:

            # Get current altitude
            et = spice.str2et(current_time.strftime("%Y-%m-%d %H:%M:%S"))
            position, _ = spice.spkpos(spacecraft, et, "BC_MSO", "NONE", "MERCURY")
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

            # if the number of apoapses is greater than the number of orbits
            # we must remove the furthest apoapsis until they are equal
            while len(apoapsis_altitudes) > number_of_orbits_to_include:

                if plot:
                    plt.plot(times, altitudes)
                    plt.scatter(apoapsis_times, apoapsis_altitudes)
                    plt.axvline(dt.datetime(year=2011, month=4, day=11, hour=5))
                    plt.show()

                # find the furthest one from the start time
                # it will be at one of the ends
                first_apoapsis_time = apoapsis_times[0]
                last_apoapsis_time = apoapsis_times[-1]

                midpoint = start_time + (end_time - start_time) / 2

                first_time_difference = abs(first_apoapsis_time - midpoint)
                last_time_difference = abs(last_apoapsis_time - midpoint)

                if first_time_difference > last_time_difference:
                    # remove first
                    apoapsis_times = np.delete(apoapsis_times, 0)
                    apoapsis_altitudes = np.delete(apoapsis_altitudes, 0)

                elif last_time_difference > first_time_difference:
                    # remove last
                    apoapsis_times = np.delete(apoapsis_times, -1)
                    apoapsis_altitudes = np.delete(apoapsis_altitudes, -1)

                else:
                    raise ValueError(
                        "Cannot reduce apoapsis list from 1 orbit. Instead, use trajectory.Get_Nearest_Apoapsis"
                    )

        return apoapsis_altitudes, apoapsis_times


def Get_Nearest_Apoapsis(
    time: dt.datetime,
    time_delta: dt.timedelta = dt.timedelta(minutes=1),
    time_limit: dt.timedelta = dt.timedelta(hours=12),
    plot: bool = False,
    spacecraft: str = "MESSENGER",
) -> tuple[dt.datetime, float]:
    """Finds closest apoapsis to input time.

    Parameters
    ----------
    time : datetime.datetime
        The time to query around.

    time_delta : datetime.timedelta, {datetime.timedelta(minutes=1)}, optional
        The time resolution of the search.

    time_limit : datetime.timedelta, {datetime.timedelta(hours=12)}, optional
        The maximum time to search before and after `time`.

    plot : bool, {False}, optional
        Produces a plot for debugging purposes.

    spacecraft : str, {'MESSENGER'}, optional
        Which spacecraft's orbit to query.


    Returns
    -------
    apoapsis_time : datetime.datetime
        The dates and times of each apoapsis found.

    apoapsis_altitude : float
        The altitude of each apoapsis found.
    """
    with spice.KernelPool(User.METAKERNEL):
        apoapsis_altitude: float = 0
        apoapsis_time: dt.datetime = time

        # Get all position data within time +- time_delta
        search_start = time - time_limit
        search_end = time + time_limit

        current_time = search_start

        altitudes = []
        times = []

        while current_time < search_end:

            # Get current altitude
            et = spice.str2et(current_time.strftime("%Y-%m-%d %H:%M:%S"))
            position, _ = spice.spkpos(spacecraft, et, "BC_MSO", "NONE", "MERCURY")
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

        if plot:
            plt.plot(times, altitudes)
            plt.scatter(
                np.array(times)[peak_indices], np.array(altitudes)[peak_indices]
            )
            plt.axvline(time)
            plt.show()

        apoapsis_time = times[closest_apoapsis_index]
        apoapsis_altitude = altitudes[closest_apoapsis_index]

        return apoapsis_time, apoapsis_altitude


def Get_Grazing_Angle(crossing, function: str = "bow shock", return_vectors: bool = False, verbose: bool = False):
    """
    We find the closest position on the Winslow (2013) average BS and MP model
    Assuming any expansion / compression occurs parallel to the normal vector
    of the curve, the vector to the closest point on the bow shock to MESSENGER
    is parallel with the bow shock normal at that closest point

    We then compare this vector, with the velocity vector of the spacecraft.
    """

    start_position = (
        traj.Get_Position(
            "MESSENGER",
            crossing["Start Time"] + (crossing["End Time"] - crossing["Start Time"]) / 2,
            frame="MSM",
            aberrate=True,
        )
        / Constants.MERCURY_RADIUS_KM
    )

    next_position = (
        traj.Get_Position(
            "MESSENGER",
            crossing["Start Time"] + (crossing["End Time"] - crossing["Start Time"]) / 2
                                   + dt.timedelta(seconds=1),
            frame="MSM",
            aberrate=True,
        )
        / Constants.MERCURY_RADIUS_KM
    )

    cylindrical_start_position = np.array([start_position[0], np.sqrt(start_position[1] ** 2 + start_position[2] ** 2)])
    cylindrical_next_position = np.array([next_position[0], np.sqrt(next_position[1] ** 2 + next_position[2] ** 2)])

    cylindrical_velocity = cylindrical_next_position - cylindrical_start_position

    # normalise velocity
    cylindrical_velocity /= np.sqrt( np.sum(cylindrical_velocity ** 2) )

    match function:
        case "bow shock":
            # Winslow+ (2013) parameters
            initial_x = 0.5
            psi = 1.04
            p = 2.75

            L = psi * p

            phi = np.linspace(0, 2 * np.pi, 10000)
            rho = L / (1 + psi * np.cos(phi))

            # Cylindrical coordinates (X, R)
            bow_shock_x_coords = initial_x + rho * np.cos(phi)
            bow_shock_r_coords = rho * np.sin(phi)

            boundary_positions = np.array(
                [bow_shock_x_coords, bow_shock_r_coords]
            ).T

        case "magnetopause":
            # Winslow+ (2013) parameters

            sub_solar_point = 1.45  # radii
            alpha = 0.5

            phi = np.linspace(0, 2 * np.pi, 10000)
            rho = sub_solar_point * (2 / (1 + np.cos(phi))) ** alpha

            # Cylindrical coordinates (X, R)
            magnetopause_x_coords = rho * np.cos(phi)
            magnetopause_r_coords = rho * np.sin(phi)

            boundary_positions = np.array(
                [magnetopause_x_coords, magnetopause_r_coords]
            ).T

        case _:
            raise ValueError( f"Invalid function choice: {function}. Options are 'bow shock', 'magnetopause'.")


    # This is setup is faster than iterrating through the points.
    # O(logN) vs O(N)
    kd_tree = scipy.spatial.KDTree(boundary_positions)
    
    _, index = kd_tree.query(cylindrical_start_position)
    closest_position = index

    # Get the normal vector of the BS at this point
    # This is just the normalised vector between the spacecraft and the closest point
    normal_vector = boundary_positions[closest_position] - cylindrical_start_position

    normal_vector = normal_vector / np.sqrt(np.sum(normal_vector**2))

    grazing_angle = np.arccos(
                        np.dot(normal_vector, cylindrical_velocity)
                        / (np.sqrt(np.sum(normal_vector**2)) * np.sqrt( np.sum(cylindrical_velocity ** 2) ))
                    )
    grazing_angle = Constants.RADIANS_TO_DEGREES(grazing_angle)

    # If the grazing angle is greater than 90, then we take 180 - angle as its from the other side
    # This occurs as we don't make an assumption as to what side of the model boundary we are.
    # i.e. we could be referencing the normal, or the anti-normal.

    if grazing_angle > 90:

        # If the angle is greater than 90 degrees, we have the normal vector
        # the wrong way around.
        grazing_angle = 180 - grazing_angle
        normal_vector = -normal_vector

    if verbose:
        print(f"Crossing Start Time: {crossing['Start Time']}")
        print(f"Crossing Type: {crossing['Type']}")
        print(f"Spacecraft Position: {cylindrical_start_position}")
        print(f"Closest Boundary Point: {boundary_positions[closest_position]}")
        print(f"Normal Vector (MSM): {normal_vector}")
        print(f"Velocity Vector (MSM): {cylindrical_velocity}")
        print(f"Grazing Angle: {grazing_angle:.3f} deg.")

    if return_vectors:
        return grazing_angle, normal_vector, cylindrical_velocity

    return grazing_angle
