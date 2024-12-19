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

    start_time = dt.datetime.strptime("2011-10-15 14:00:00", "%Y-%m-%d %H:%M:%S")
    end_time = dt.datetime.strptime("2011-10-15 16:00:00", "%Y-%m-%d %H:%M:%S")

    data = mag.Load_Between_Dates()
