Contributing
============

Contributing to hermpy
----------------------

hermpy is open source and community driven!

Feature requests, bugs and other issues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you encounter a bug in the code, or something else which needs changing (i.e. documentation), please create an `issue`_ on Github. When making an issue, be as descriptive as possible.

If there is an additional feature you think should be apart of hermpy, please also create an issue.

.. _`issue`: https://github.com/daraghhollman/hermpy/issues

Contributing Code
^^^^^^^^^^^^^^^^^

The easiest way to contribute code to hermpy is to first **fork the repository**, and then clone to your local computer:

.. code-block:: shell

   git clone https://github.com/<your-username>/hermpy/


Create a new branch and start working on your changes!

.. code-block:: shell

   # e.g.
   git branch feat/my-cool-new-feature

In hermpy, we use `uv`_ to manage package dependancies. When testing your code additions, it can be helpful to use uv to run Python to ensure a reproducable environment.

.. _`uv`: https://docs.astral.sh/uv/

.. code-block:: shell

   uv run python <my-cool-script>


When you are finished making changes and have tested your code, you will need to commit and push your changes to your fork, afterwards, make a `pull request`_. There, we can see your changes, and suggest improvements, before finally merging the code into the repository, to be available in the next version of hermpy.

.. _`pull request`: https://github.com/daraghhollman/hermpy/pulls
