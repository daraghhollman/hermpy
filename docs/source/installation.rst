Installation
============

Overview
********

Before installing ``hermpy``, we recommend you set up a Python environment which is **isolated** from your system Python installation, or any other dedicated Python environment. Hermpy has dependencies, which can interfere with requirements in those environments which could lead to issues.

For this installation guide, we use the Python standard library `venv <https://docs.python.org/3/library/venv.html>`_ module. Alternatives are available, such as the `conda <https://docs.conda.io/en/latest/>`_ package manager.


Installing a Python Environment
*******************************

Assuming you have a Python installation on your system, you can create a new virtual environment as follows:

.. code-block:: bash

   python -m venv /path/to/new/virtual/environment

The way you access your virtual environment will differ system, on UNIX-based systems using bash/zsh it can be done as follows:

.. code-block:: bash

   source <venv>/bin/activate


On Windows via cmd.exe:

.. code-block:: console

   <venv>\Scripts\activate.bat


Installing Hermpy
*****************

Hermpy and its dependancies can be installed using pip. First clone the repository:

.. code-block:: bash

   git clone https://github.com/daraghhollman/hermpy

Then install using:

.. code-block:: bash

   pip install ./hermpy/
