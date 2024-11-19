
class Constants:
    # All are in base SI units
    MERCURY_RADIUS = 2_439_700 # meters
    MERCURY_RADIUS_KM = MERCURY_RADIUS / 1_000 # kilometers

    DIPOLE_OFFSET_KM = 497 # kilometerss
    DIPOLE_OFFSET_RADII = DIPOLE_OFFSET_KM / MERCURY_RADIUS_KM

    MERCURY_SEMI_MAJOR_AXIS = 57_909_050 * 1_000 # meters
    SOLAR_MASS = 1.9891e30 # kilograms

    SOLAR_WIND_SPEED_AVG = 400_000 # meters / second

    G = 6.6743e-11 # N m^2 / kg^2

