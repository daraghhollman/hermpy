import spiceypy as spice


def Get_Trajectory(spacecraft: str, dates: list[str], metakernel: str, steps=4000, frame="MSO"):
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
            positions[:,2] += 479
            return positions

    return positions
