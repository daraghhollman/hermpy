import datetime as dt

import numpy as np


def Load_Messenger(file_paths: list[str]):
    """Reads data from a list of file paths

    Uses pandas to load and combine multiple FIPS data files


    Parameters
    ----------
    file_paths : list[str]
        A list containing the absolute file paths to be loaded.


    Returns
    -------
    out : list[tuple]
        Structured array with rows as follows:

        [0]       Met:       float
        [1]       UTC:       dt.datetime
        [2]       Quality:   int
        [3]       Mode:      int
        [4:67]    Start:     float
        [67:130]  Stop:      float
        [130:193] VE:        float
        [193:256] Proton:    float
        [256:319] EP:        float

    """

    multi_file_data = {
        "dates":           [],
        "start_energies":  [],
        "stop_energies":   [],
        "ve_energies":     [],
        "proton_energies": [],
        "ep_energies":     [],
    }

    for path in file_paths:

        # Create structured array from data
        # This type is a list of tuples for each row
        dates = np.genfromtxt(
            path,
            dtype=None,
            usecols=[1],
            converters={1: lambda s: dt.datetime.strptime(s, "%Y-%jT%H:%M:%S.%f")},
        )
        start_energies = np.genfromtxt(
            path, dtype=float, usecols=np.arange(4, 67).tolist()
        )
        stop_energies = np.genfromtxt(
            path, dtype=float, usecols=np.arange(67, 130).tolist()
        )
        ve_energies = np.genfromtxt(
            path, dtype=float, usecols=np.arange(130, 193).tolist()
        )
        proton_energies = np.genfromtxt(
            path, dtype=float, usecols=np.arange(193, 256).tolist()
        )
        ep_energies = np.genfromtxt(
            path, dtype=float, usecols=np.arange(256, 319).tolist()
        )

        multi_file_data["dates"].append(dates)
        multi_file_data["start_energies"].append(start_energies)
        multi_file_data["stop_energies"].append(stop_energies)
        multi_file_data["ve_energies"].append(ve_energies)
        multi_file_data["proton_energies"].append(proton_energies)
        multi_file_data["ep_energies"].append(ep_energies)

    return multi_file_data
