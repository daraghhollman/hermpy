from .utils import *

# Check directories all all correct
import os
import warnings

paths_to_test = [
    User.METAKERNEL,
    *User.DATA_DIRECTORIES.values(),
    *User.CROSSING_LISTS.values(),
]

for path in paths_to_test:
    if os.path.exists(path):
        continue

    else:
        warnings.warn("Paths not set in hermpy.utils.User, may cause errors.")
