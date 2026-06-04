"""
Specific checks for os
"""

import platform


def get_multiprocessing_start_method() -> str:
    """Returns desired start method for multiprocessing tasks (downloads).

    Windows -> "spawn"

    Unix    -> "fork"
        Different from Python 3.14 default: "forkserver", see #12:
        https://github.com/daraghhollman/hermpy/pull/12
    """

    operating_system = platform.system()

    if operating_system == "Windows":
        return "spawn"

    else:
        return "fork"
