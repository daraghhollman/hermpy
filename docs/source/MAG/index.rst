.. _hermpy-mag:

******************
MAG (`hermpy.mag`)
******************

Introduction
============

`hermpy.mag` contains routines for the loading, cleaning, and processing of magnetometer data from the MESSENGER spacecraft. The data format is generalised to enable the addition of BepiColombo and further spacecraft as their data becomes publically available. 

Getting Started
===============

Downloading Data
****************

To get started using MAG data, you must have some data downloaded. `hermpy` expects the data directory to be in the form:

.. code-block:: bash

    ├── 2011
    │   ├── 03_MAR
    │   ├── 04_APR
    │   ├── 05_MAY
    │   ├── 06_JUN
    │   ├── 07_JUL
    │   ├── 08_AUG
    │   ├── 09_SEP
    │   ├── 10_OCT
    │   ├── 11_NOV
    │   └── 12_DEC
    ├── 2012
    │   ├── 01_JAN
    │   ├── 02_FEB
    │   ├── 03_MAR
    │   ├── 04_APR
    .   .
    .   .
    .   .
    └── 2015
        ├── 01_JAN
        ├── 02_FEB
        ├── 03_MAR
        └── 04_APR


with each month's directory containing the MAG files as downloaded from the `calibrated PDS/PPI for MESSENGER <https://search-pdsppi.igpp.ucla.edu/search/view/?f=yes&id=pds://PPI/mess-mag-calibrated/data/mso>`_

To aid the user, `hermpy.utils` contains a function to download and store the data in the required format, for any of the data resolutions: :ref:`hermpy-utils-Download_MESSENGER_MAG`.


Loading Data
************

MAG data can be loaded using the :ref:`hermpy-mag-Load_Between_Dates` function. An example of this is as follows:

.. code-block:: python

    import datetime as dt

    from hermpy import mag
    from hermpy.utils import User

    start_time = dt.datetime.strptime("2011-10-15 14:00:00", "%Y-%m-%d %H:%M:%S")
    end_time = dt.datetime.strptime("2011-10-15 16:00:00", "%Y-%m-%d %H:%M:%S")

    # Load_Between_Dates() required a path to a directory containing the data to search,
    # along with a start and end datetime object.
    data = mag.Load_Between_Dates(User.DATA_DIRECTORIES["MAG"], start_time, end_time)


Information pointing to the data directory, and other useful user settings around found in the :ref:`hermpy-utils-User` class.

The returned object is a `pandas dataframe <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html>`_ with the following columns:

.. list-table:: MAG Data Object
   :widths: 25 25 50
   :header-rows: 1

   * - key
     - dtype
     - notes

   * - date
     - datetime.datetime
     - The UTC time of measurements

   * -
     -
     -

   * - \|B\|
     - float
     - Total magnetic field strength

   * - Bx
     - float
     - X component of the magnetic field

   * - By
     - float
     - Y component of the magnetic field

   * - Bz
     - float
     - Z component of the magnetic field

   * -
     -
     -

   * - X MSO (km)
     - float
     - X position in the Mercury Solar Orbital (MSO) coordinate system, in kilometers.

   * - Y MSO (km)
     - float
     - Y position in the MSO coordinate system, in kilometers.

   * - Z MSO (km)
     - float
     - Z position in the MSO coordinate system, in kilometers.

   * -
     -
     -

   * - X MSO (radii)
     - float
     - X position in the MSO coordinate system, in Mercury radii.

   * - Y MSO (radii)
     - float
     - Y position in the MSO coordinate system, in radii.

   * - Z MSO (radii)
     - float
     - Z position in the MSO coordinate system, in radii.

   * -
     -
     -

   * - X MSM (km)
     - float
     - X position in the Mercury Solar Magnetic (MSM) coordinate system, in kilometers.

   * - Y MSM (km)
     - float
     - Y position in the MSM coordinate system, in kilometers.

   * - Z MSM (km)
     - float
     - Z position in the MSM coordinate system, in kilometers.

   * -
     -
     -

   * - X MSM (radii)
     - float
     - X position in the MSM coordinate system, in Mercury radii.

   * - Y MSM (radii)
     - float
     - Y position in the MSM coordinate system, in radii.

   * - Z MSM (radii)
     - float
     - Z position in the MSM coordinate system, in radii.

   * -
     -
     -

   * - range (MSO)
     - float
     - The distance from the spacecraft to Mercury, in kilometers.
