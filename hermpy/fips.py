import datetime as dt

import numpy as np


def Load_Messenger(file_paths: list[str]):
    """Reads data from a list of file paths

    Uses numpy to load and combine multiple FIPS data files


    Parameters
    ----------
    file_paths : list[str]
        A list containing the absolute file paths to be loaded.


    Returns
    -------
    out : dict{
        "dates" : list[datetime.datetime]
            The date and time of each measurement.

        "start_energies" : numpy.ndarray[float]
            Desc.

        "stop_energies" : numpy.ndarray[float]
            Desc.

        "proton_energies" : numpy.ndarray[float]
            The proton spectra with time on the long axis

        "ep_energies" : numpy.ndarray[float]

    }
    """

    multi_file_data = {
        "dates": [],
        "start_energies": [],
        "stop_energies": [],
        "ve_energies": [],
        "proton_energies": [],
        "ep_energies": [],
    }

    for path in file_paths:

        # Create structured array from data
        # This type is a list of tuples for each row
        dates = np.genfromtxt(
            path,
            dtype=None,
            usecols=[1],
            converters={1: lambda s: dt.datetime.strptime(s, "%Y-%jT%H:%M:%S.%f")},
        ).tolist()
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

    # We squeeze the list of arrays to combine them into one array.
    multi_file_data["dates"] = np.squeeze(multi_file_data["dates"])
    multi_file_data["start_energies"] = np.squeeze(multi_file_data["start_energies"])
    multi_file_data["stop_energies"] = np.squeeze(multi_file_data["stop_energies"])
    multi_file_data["ve_energies"] = np.squeeze(multi_file_data["ve_energies"])
    multi_file_data["proton_energies"] = np.squeeze(multi_file_data["proton_energies"])
    multi_file_data["ep_energies"] = np.squeeze(multi_file_data["ep_energies"])
    
    return multi_file_data



def Strip_Data(data: dict, start: dt.datetime, stop: dt.datetime):
    """Shortens the array to only include times between two given times


    Parameters
    ----------
    data : dict
        The data to be shortened, as created by Load_Messenger().
        Although, any similarly formatted data will work.

    start : datetime.datetime
        The date and time to start including data.
        Anything before this time will be excluded.

    end : datetime.datetime
        The date and time to stop including data.
        Anything after this time will be excluded.


    Returns
    -------
    out : dict
        A copy of the input data dictionary, shortened to only
        include the data between the start and stop times.
    """

    # First we iterrate through the dates list in the data dictionary
    # to find the indices which are outside of the time range.
    dates = data["dates"]

    indices_to_remove: list[int] = []
    for i, date in enumerate(dates):
        if (date < start) or (date > stop):
            # Add to indices list
            indices_to_remove.append(i)

        else:
            continue


    data["dates"] = np.delete(data["dates"], indices_to_remove)
    data["start_energies"] = np.delete(data["start_energies"], indices_to_remove, 0)
    data["stop_energies"] = np.delete(data["stop_energies"], indices_to_remove, 0)
    data["ve_energies"] = np.delete(data["ve_energies"], indices_to_remove, 0)
    data["proton_energies"] = np.delete(data["proton_energies"], indices_to_remove, 0)
    data["ep_energies"] = np.delete(data["ep_energies"], indices_to_remove, 0)

    return data
