Importing Hermpy and Sub-modules
==================================

Hermpy functionality resides mostly within various sub-modules. Importing `hermpy` as:

.. code-block:: python

   import hermpy

is not useful. Instead, it is best practice to import the required sub-modules with the following syntax:

.. code-block:: python

   from hermpy import submodule

or

.. code-block:: python

   import hermpy.submodule as submodule

In some cases, the required functionality is containined in a small number of classes. In those cases, the class(es) can be directly imported, e.g.:

.. code-block:: python

   from hermpy.utils import User, Constants


Getting Started with Sub-modules
********************************

As each sub-module contains different functionality, each sub-module has its own documentation and getting started guide. These can be found in the :ref:`user-guide`.
