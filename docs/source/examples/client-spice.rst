Using ClientSPICE to Manage SPICE Kernels
==========================================

This example demonstrates how to use :class:`hermpy.net.ClientSPICE` to
fetch and manage SPICE kernels, and how to compute spacecraft positions using
`spiceypy <https://spiceypy.readthedocs.io/en/main/>`_.

.. contents:: On this page
   :local:
   :depth: 2


Prerequisites
-------------

This example requires the following imports:

.. code-block:: python

   import datetime as dt
   import spiceypy as spice
   from hermpy.net import ClientSPICE


Setting up the client
---------------------

:class:`~hermpy.net.ClientSPICE` is a caching client that handles the
fetching of SPICE kernels. Instantiate one before opening any kernel context:

.. code-block:: python

   spice_client = ClientSPICE()

A set of default kernels is bundled with ``hermpy`` and will be loaded
automatically. Additional kernels can be registered at any time by updating
:attr:`~hermpy.net.ClientSPICE.KERNEL_LOCATIONS`.

.. note::

   If you believe your kernel additions would be a useful permanent inclusion
   for all users, please open a pull request.


Adding custom kernels
---------------------

The example below registers the BepiColombo frames kernel, which exposes
reference frames such as ``BC_MSO_AB``:

.. code-block:: python

   spice_client.KERNEL_LOCATIONS.update(
       {
           "BepiColombo Frames": {
               "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
               "DIRECTORY": "pds/pds4/bc/bc_spice/spice_kernels/fk/",
               "PATTERNS": ["bc_sci_v12.tf"],
           }
       }
   )

``KERNEL_LOCATIONS`` is a plain :class:`dict`, so standard Python mapping
operations (``update``, direct key assignment, etc.) all work as
expected.


Loading kernels and computing a position
-----------------------------------------

There are two equivalent ways to open a kernel context. Both approaches call
:meth:`~hermpy.net.ClientSPICE.fetch` under the hood, which downloads any
missing kernels and returns a list of local paths.


Using ``spice.KernelPool`` directly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can pass the fetched kernel paths straight to
:func:`spiceypy.KernelPool`:

.. code-block:: python

   with spice.KernelPool(spice_client.fetch()):
       et = spice.datetime2et(dt.datetime(2012, 6, 1))
       position, _ = spice.spkpos("MESSENGER", et, "BC_MSO_AB", "NONE", "Mercury")
       print(position)

:func:`spiceypy.datetime2et` converts a standard :class:`datetime.datetime`
object to an ephemeris time (ET) scalar, which is the time format expected by
most SPICE routines.

:func:`spiceypy.spkpos` returns the position of the target body
(``"MESSENGER"``) relative to the observer (``"Mercury"``), expressed in the
requested reference frame (``"BC_MSO_AB"``), with no aberration correction
(``"NONE"``). The second return value — the one-way light time — is discarded
with ``_`` here.


Using ``spice_client.KernelPool`` (preferred)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:meth:`~hermpy.net.ClientSPICE.KernelPool` is a convenience context manager
that calls :meth:`~hermpy.net.ClientSPICE.fetch` and forwards the result to
:func:`spiceypy.KernelPool` for you:

.. code-block:: python

   with spice_client.KernelPool():
       et = spice.datetime2et(dt.datetime(2012, 6, 1))
       position, _ = spice.spkpos("MESSENGER", et, "BC_MSO_AB", "NONE", "Mercury")
       print(position)

Both blocks produce identical output. The ``spice_client.KernelPool()`` form
is preferred because it keeps the fetch-and-load step implicit and avoids
repeating ``spice_client.fetch()`` at every call site.


Complete example
----------------

.. exec_code::

   import datetime as dt
   import spiceypy as spice
   from hermpy.net import ClientSPICE

   spice_client = ClientSPICE()

   spice_client.KERNEL_LOCATIONS.update(
       {
           "BepiColombo Frames": {
               "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
               "DIRECTORY": "pds/pds4/bc/bc_spice/spice_kernels/fk/",
               "PATTERNS": ["bc_sci_v12.tf"],
           }
       }
   )

   with spice_client.KernelPool():
       et = spice.datetime2et(dt.datetime(2012, 6, 1))
       position, _ = spice.spkpos("MESSENGER", et, "BC_MSO_AB", "NONE", "Mercury")
       print(position)

which gives MESSENGER's position in kilometers in the (average) aberated
Mercury-Solar-Orbital reference frame.


See also
--------

- :doc:`/examples/index` — full examples gallery
- :class:`hermpy.net.ClientSPICE` — API reference
- `spiceypy documentation <https://spiceypy.readthedocs.io/en/main/>`_
- `NAIF SPICE toolkit <https://naif.jpl.nasa.gov/naif/toolkit.html>`_
