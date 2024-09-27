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

        quality = np.genfromtxt(path, dtype=int, usecols=[2])
        mode = np.genfromtxt(path, dtype=int, usecols=[3])

        if quality.any() != 0:
            # A quality value != 0 is bad, we should ignore these
            # First get the indices, then only keep the rows
            indices = np.where(quality == 0)
            dates = np.array(dates)[indices].tolist()
            start_energies = start_energies[indices]
            stop_energies = stop_energies[indices]
            ve_energies = ve_energies[indices]
            proton_energies = proton_energies[indices]
            ep_energies = ep_energies[indices]

        if mode.any() != 2:
            print(set(mode.tolist()))

        multi_file_data["dates"].append(dates)
        multi_file_data["ve_energies"].append(ve_energies)
        multi_file_data["proton_energies"].append(proton_energies)
        multi_file_data["ep_energies"].append(ep_energies)

    # We squeeze the list of arrays to combine them into one array.
    for key in multi_file_data.keys():
        multi_file_data[key] = np.squeeze(multi_file_data[key])

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
    data["ve_energies"] = np.delete(data["ve_energies"], indices_to_remove, 0)
    data["proton_energies"] = np.delete(data["proton_energies"], indices_to_remove, 0)
    data["ep_energies"] = np.delete(data["ep_energies"], indices_to_remove, 0)

    return data


def Get_Calibration() -> list[float]:
    """Returns calibration for FIPS energy channels

    Currently 'calibration' is assumed constant for all data modes.
    This is accepted within the literature and scientific community.

    
    Returns
    -------
    out : list[float]
        A list with an E/Q value for each of the 64 energy channels.

    """


    # This calibration is from the most recent calibration file
    # on the pds. This is column one.
    # Found here: https://search-pdsppi.igpp.ucla.edu/search/view/?f=yes&id=pds://PPI/mess-epps-fips-calibrated/calibration/FIPA_E2014153CDR_V2&o=1
    calibration = [13.5774, 12.3322, 11.2011, 10.1738, 9.2407,
                   8.3930, 7.6233, 6.9243, 6.2892, 5.7121,
                   5.1884, 4.7126, 4.2802, 3.8877, 3.5310, 
                   3.2074, 2.9131, 2.6459, 2.4034, 2.1830,
                   1.9828, 1.8007, 1.6358, 1.4855, 1.3493, 
                   1.2255, 1.1133, 1.0110, 0.9184, 0.8343, 
                   0.7576, 0.6880, 0.6251, 0.5677, 0.5156,
                   0.4682, 0.4255, 0.3863, 0.3510, 0.3189,
                   0.2896, 0.2631, 0.2388, 0.2170, 0.1970,
                   0.1789, 0.1627, 0.1478, 0.1340, 0.1219, 
                   0.1107, 0.1004, 0.0851, 0.0729, 0.0611,
                   0.0489, 0.0371, 0.0249, 0.0131, 0.0087,
                   0.0087, 0.0087, 0.0087, 0.0087]

    return calibration
