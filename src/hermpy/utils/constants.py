import astropy.units as u

# Define Mercury Radius as a named unit
mercury_radius = u.def_unit(
    "Mercury Radii",
    2_439_700 * u.m,
    format={"latex": "R_M", "unicode": "R_M"},
)

# Register it so .to() and equivalencies work globally
u.add_enabled_units([mercury_radius])


class Constants:
    MERCURY_RADIUS = 1 * mercury_radius
    DIPOLE_OFFSET = 479 * u.km
    DIPOLE_OFFSET_RADII = DIPOLE_OFFSET.to(mercury_radius)

    MERCURY_SEMI_MAJOR_AXIS = 57_909_050 * u.km
    SOLAR_MASS = 1.9891e30 * u.kg

    SOLAR_WIND_SPEED_AVG = 400_000 * u.m / u.s

    G = 6.6743e-11 * u.N * u.m**2 / u.kg**2
