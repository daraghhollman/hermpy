# Mercury Tools

A repository I've adapted from similar code found [here](https://github.com/DIASPlanetary/MESSENGER_Tools) to perform science with data from space missions around Mercury.

## mag.py

A library of functions to load and manipulate magnetic field data.

### Usage

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

