# HERMPY - A tool-belt for space science at Mercury

Tools for aiding in the handling of data and the creation of publication ready plots from spacecraft around Mercury.

## Installation

The hermpy package can be installed manually in the following way:

```shell
git clone https://github.com/daraghhollman/hermpy
cd hermpy/
pip install .
```

Further setup is required. Paths in `hermpy/utils/utils.py, class: User` must
be updated to locations of your choosing. MESSENGER MAG data can be
automatically downloaded using `hermpy.utils.User.Download_MESSENGER_MAG()`,
however, it is currently quicker to download zip files using the
[PDS](https://search-pdsppi.igpp.ucla.edu/search/view/?f=yes&id=pds://PPI/mess-mag-calibrated/data/mso),
[doi](https://doi.org/10.17189/1522385). The directories however should match the following format:

```
.
├── 2011
│   ├── 03_MAR
│   │   ├── MAGMSOSCIAVG11082_01_V08.TAB
│   │   ├── MAGMSOSCIAVG11083_01_V08.TAB
│   │   ... etc.
│   ├── 04_APR
│   ├── 05_MAY
│   ├── 06_JUN
│   ├── 07_JUL
│   ├── 08_AUG
│   ├── 09_SEP
│   ├── 10_OCT
│   ├── 11_NOV
│   └── 12_DEC
├── 2012
│   ├── 01_JAN
│   ├── 02_FEB
│   ├── 03_MAR
│   ├── 04_APR
│   ├── 05_MAY
...
```

The Philott et al. (2020) crossing list can be downloaded from supplementary
information [here](https://doi.org/10.1029/2019JA027544). The path must be
updated in `hermpy/utils/utils.py`

## Usage

Examples can be found in the `examples/` directory. Due to some recent breaking
changes, not all of these examples will work out of the box. If you have issues
running an example script, please report it as a Github issue!

## References

Winslow, R. M., B. J. Anderson, C. L. Johnson, J. A. Slavin, H. Korth, M. E.
Purucker, D. N. Baker, and S. C. Solomon (2013), Mercury’s magnetopause and bow
shock from MESSENGER Magnetometer observations, J. Geophys. Res. Space Physics,
118, 2213–2227, doi:10.1002/jgra.50237

Philpott, L. C., Johnson, C. L., Anderson, B. J., & Winslow, R. M. (2020). The
shape of Mercury's magnetopause: The picture from MESSENGER magnetometer
observations and future prospects for BepiColombo. Journal of Geophysical
Research: Space Physics, 125, e2019JA027544.
https://doi.org/10.1029/2019JA027544

Annex et al., (2020). SpiceyPy: a Pythonic Wrapper for the SPICE Toolkit.
Journal of Open Source Software, 5(46), 2050,
https://doi.org/10.21105/joss.02050

Acton, C.H.; "Ancillary Data Services of NASA's Navigation and Ancillary
Information Facility;" Planetary and Space Science, Vol. 44, No. 1, pp. 65-70,
1996.
