# Mercury Tools

A repository I've adapted from similar code found [here](https://github.com/DIASPlanetary/MESSENGER_Tools) to perform science with data from space missions around Mercury.

## Docs

### plotting_tools.py

A library of functions to assist in creating publication ready plots. Currently, this solely includes the plotting of Mercury onto any matplotlib axis, along with pulling the positions of a given spacecraft between two dates.

#### Usage

A basic usage would be as follows:

```python
# metakernel created using autometa
metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"

# we are going to get positions between these two dates
dates = ["2012-06-10", "2012-06-20"]

positions = plotting_tools.Get_Trajectory("Messenger", dates, metakernel)

positions /= 2439.7 # convert from km to radii

fig, ax = plt.subplots()

ax.plot(positions[:, 0], positions[:, 1])

# Plotting mercury with the left side shaded
plotting_tools.Plot_Mercury(ax, shaded_hemisphere="left")

ax.set_aspect("equal")

plt.show()
```

#### Functions

plotting_tools.**Get_Trajectory**(spacecraft, dates, metakernel, steps=4000)

Pulls position data for a given spacecraft and corresponding metakernel.

**Parameters:**
* spacecraft : string - the name of the required spacecraft. e.g. "Messenger"
* dates : list\[string\] - A list of length 2, containing a start and finish date as strings. e.g. \["2012-06-10", "2012-06-20"\]
* metakernel : string - A path to the relevant SPICE metakernel for the given spacecraft. Metakernels can be easily generated using [AutoMeta](https://github.com/mjrutala/AutoMeta).
* steps : int, *default* 4000 - Number of positions to return between the two dates. 

------------------------------------------------------------

plotting_tools.**Plot_Mercury(ax, shaded_hemisphere="none", offset=(0,0))

Adds a circle representing Mercury at (0,0) + an optional offset.

**Parameters:**
* ax : matplotlib axis
* shaded_hemisphere : string - Which hemisphere to shade, options are: left, right, top, or bottom.
* offset : tuple\[float, float\] - Apply an offset to the centre of Mercury. Useful when working in none Mercury-centric frames such as MSM / MSM'.

### mag.py

A library of functions to load and manipulate magnetic field data.

#### Usage

A basic usage would be as follows:

```python
import mag

data = mag.Load_Messenger([file1, file2, file3, ...])


start = dt.datetime(year=2014, month=1, day=1, hour=0)
end = dt.datetime(year=2014, month=1, day=1, hour=10)

data = mag.StripData(data, start, end)
```

This data object is a Pandas DataFrame, and has the following columns:

* **date**:  a datetime object of the time of the measurement
* **frame**: the current coordinate system
* **eph_x**: the x coordinate of the spacecraft (km)
* **eph_y**: the y coordinate of the spacecraft (km)
* **eph_z**: the z coordinate of the spacecraft (km)
* **range**: the distance of the spacecraft from Mercury (km)
* **mag_x**: the magnetic field strength in x (nt)
* **mag_y**: the magnetic field strength in y (nt)
* **mag_z**: the magnetic field strength in z (nt)
* **mag_total**: the total magnetic field strength (nt)

**StripData** shortens the data from the full files down to only between the start and end times. 

This library also contains function to convert to MSM frames via:

```python
data = mag.MSO_TO_MSM(data)

# and to convert back
# warning: the data does not know which frame it in and will be incorret if these actions are repeated

data = mag.MSM_TO_MSM(data)
```

and also to account for solar wind aberration angles:

```python
data = mag.AdjustForAberration(data)
```

