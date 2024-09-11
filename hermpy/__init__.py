from importlib.metadata import version as _version, PackageNotFoundError
try:
    __version__ = _version(__name__)
except PackageNotFoundError:
    pass

import hermpy.trajectory
import hermpy.mag
import hermpy.plotting_tools
import hermpy.boundary_crossings
