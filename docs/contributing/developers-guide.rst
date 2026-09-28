Developers Guide
================

Getting started
---------------
The best way to start contributing is to look at known `issues`_. Each issue will have a series of labels to provide more information at a glance. If you decide to start working on an issue, please add a comment to let others know that it is being worked on!

.. _`issues`: https://github.com/daraghhollman/hermpy/issues

Using uv for reproducability
----------------------------

Most important when starting development is to setup a reproducible coding environment. Historically, this has been done using tools like `Conda`_, however, we recommend the use of `uv`_.

uv manages the Python environment through two key files:

* `pyproject.toml`_
* uv.lock

The ``pyproject.toml`` file stores information about the project, including rules for dependencies. The ``uv.lock`` file (referred to generally as a 'lockfile') is automatically generated from the ``pyproject.toml`` file and outlines specifically what versions of Python and packages were used to build the environment. The lockfile is read by uv when running Python, and builds the *exact* environment which was used when the file was generated.

.. _`Conda`: https://conda.org/
.. _`uv`: https://docs.astral.sh/uv/
.. _`pyproject.toml`: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/

`Install uv`_, and use it by prefixing any Python or other environment specific commands.

e.g. to run an example:

.. code-block:: shell

   uv run python ./src/exampless/<example-file>.py

or, to build the documentation:

.. code-block:: shell

   cd docs/
   uv run make clean
   uv run make build

.. _`Install uv`: https://docs.astral.sh/uv/getting-started/installation/

Using pre-commit for consistancy
--------------------------------

We use `pre-commit`_ tools to ensure consistent code standards. The config for pre-commit can be found in ``.pre-commit-config.yaml``. We use pre-commit hooks to lint and check the formatting of our code.

Using pre-commit is optional. We won't force code standards until the pull request stage. However, we do recommend it. Pre-commit is enabled as follows:

.. code-block:: shell

   uv run pre-commit install

``pre-commit`` will now run automatically when you run ``git commit``.

.. _`pre-commit`: https://pre-commit.com/

What happens when you make a pull request
-----------------------------------------

When you create a pull request (PR), you will be prompted with a template. This will include some guidelines at the beginning, which should be removed before submitting the PR. Each pull request should contain:

* a short but informative title
* a description of the problem
* a description of the implemented solution
* an AI assistance disclosure (included in the template)

When you submit your PR, our continuous integration (CI) will run the test-suite, check the linting and formatting of the code, and build the documentation. If any of these steps fail, there may be an issue with your code and revisions may be required. If you believe there is an issue with any of these steps, please add a comment outline this.

Before merging your code, it will need to be reviewed by one of our team to ensure that:

* the change are a worthwhile addition
* the changes are functional
* the changes are well documented and have associated tests if required

If approved, the changes will be merged (typically squashed into one commit) and included in the next version.
