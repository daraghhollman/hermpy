# HERMPY - A tool-belt for space science at Mercury

Tools for aiding in the handling of data and the creation of publication ready plots from spacecraft around Mercury.

## Installation

The hermpy package can be installed manually in the following way:

```shell
git clone https://github.com/daraghhollman/hermpy
cd hermpy/
pip install .
```

### Further Setup

MESSENGER MAG data can be automatically downloaded with:

```python
hermpy.utils.download_MESSENGER_MAG(save_directory: str)
```
however, it is possible to download files manually using the [PDS](https://search-pdsppi.igpp.ucla.edu/search/view/?f=yes&id=pds://PPI/mess-mag-calibrated/data/mso), [doi](https://doi.org/10.17189/1522385). The directories however should match the following format:

### Philpott Crossing List
Certain functions (particularly from hermpy.boundaries) require the use of a
crossing list. The Philott et al. (2020) crossing list can be downloaded from
supplementary information [here](https://doi.org/10.1029/2019JA027544). The
path must be updated in `hermpy/utils/utils.py`

### SPICE
hermpy uses SPICE to determine MESSENGER and BepiColombo ephemerides. You
require a SPICE MetaKernel appropriate for the MESSENGER mission. The
MetaKernel should refer to the appropriate MESSENGER ephemeris (spk) and frame
(fk) kernels for the period of interest, the current leap seconds kernel (lsk),
an appropriate planetary and/or satellite ephemeris kernel (spk), and an
appropriate planetary constants kernel (pck).

More information about the SPICE toolkit can be found at:
(https://naif.jpl.nasa.gov/naif/toolkit.html)

In particular, useful information for constructing a MetaKernel can be found
at: https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/kernel.html

If you don’t have your own metakernel, you can create one for MESSENGER using
this tool:
- [AutoMeta](https://github.com/mjrutala/AutoMeta)

Annex et al., (2020). SpiceyPy: a Pythonic Wrapper for the SPICE Toolkit.
Journal of Open Source Software, 5(46), 2050,
https://doi.org/10.21105/joss.02050

Acton, C.H.; "Ancillary Data Services of NASA's Navigation and Ancillary
Information Facility;" Planetary and Space Science, Vol. 44, No. 1, pp. 65-70,
1996.

## Usage

Examples can be found in the `examples/` directory. Due to some recent breaking
changes, not all of these examples will work out of the box. If you have issues
running an example script, please open a Github issue.

## References

Plotting functions utilise the Winslow et al. (2013) average bow shock and
magnetopause forms:

Winslow, R. M., B. J. Anderson, C. L. Johnson, J. A. Slavin, H. Korth, M. E.
Purucker, D. N. Baker, and S. C. Solomon (2013), Mercury’s magnetopause and bow
shock from MESSENGER Magnetometer observations, J. Geophys. Res. Space Physics,
118, 2213–2227, doi:10.1002/jgra.50237
