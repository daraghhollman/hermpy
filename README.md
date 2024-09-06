# Hermean Toolbelt

Tools for aiding in the creation of publication ready plots with data from spacecraft around Mercury.

## Installation

Pre-publishing, this package can be installed manually from source. When published, this package will be available via pypi.

```shell
git clone https://github.com/daraghhollman/HermeanToolbelt
pip install -e /path/to/this/repository/
```

## Usage

Several subpackages can be imported:
```python
from HermeanToolbelt import plotting_tools
from HermeanToolbelt import trajectory
from HermeanToolbelt import mag
```

Examples can be found in the `examples/` directory.

## References

**Average magnetosphere boundary model**

Winslow, R. M., B. J. Anderson, C. L. Johnson, J. A. Slavin, H. Korth, M. E. Purucker, D. N. Baker, and S. C. Solomon (2013), Mercury’s magnetopause and bow shock from MESSENGER Magnetometer observations, J. Geophys. Res. Space Physics, 118, 2213–2227, doi:10.1002/jgra.50237

**Boundary Crossing Lists**

Philpott, L. C., Johnson, C. L., Anderson, B. J., & Winslow, R. M. (2020). The shape of Mercury's magnetopause: The picture from MESSENGER magnetometer observations and future prospects for BepiColombo. Journal of Geophysical Research: Space Physics, 125, e2019JA027544. https://doi.org/10.1029/2019JA027544

Sun, W. (2023). Lists of Magnetopause and Bow Shock Crossings of Mercury by MESSENGER Spacecraft (August 29th, 2023) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.8298647
