Developing
==========

This section contains all the necessary information to run and build the program from source and how to contribute to the project.
For contributions to the project, please also consider our :ref:`contribution guidelines<contributing:Contributing>`.

If you run into any problems, feel free to create an issue to describe the problem.

Poetry Quick Start
------------------

This section gives you the basic commands to use Poetry to run the project.
For further information check their documentation.

You can install the package in a local virtual environment managed by Poetry with

.. code::

   $ poetry install

After that you can run commands in this environment with

.. code::

   $ poetry run $yourcommand

For example, if you want to initialize the network you run

.. code::

   $ poetry run cfgnet init $PATH_TO_REPOSITORY

where :code:`$PATH_TO_REPOSITORY` is the path to the root of the repository (i.e.  where :code:`.git` is).

Building the package
--------------------

`Poetry <https://python-poetry.org/>`_ is used to build the package.
After installing Poetry you can build the project with

.. code::

   $ poetry build

This will create a source distribution and a wheel in :code:`dist/`.

To start developing with the package you need to install `Poetry <https://python-poetry.org/>`_ and optionally Make.

Code Style
----------

`Black <https://github.com/python/black>`_ is used for code formatting.
To format your contributions, run

.. code::

    $ black src tests

Makefile
--------

This repository also provides a Makefile for convenience.
The default rule (:code:`install`) will install the package with Poetry.

In addition to there are the following rules:

* :code:`test`: Run the tests. Will be checked in CI, too.
* :code:`linter`: Run the linters. Will be checked in CI, too.
* :code:`mypy`: Run mypy. Will be checked in CI, too.
* :code:`codeformat`: Format all source and test files with Black.
* :code:`distribution`: Build the source distribution and wheel packages.
* :code:`clean`: Removes all the local build files. Note that this does not include anything in the virtual environment to prevent conflicts with your Poetry workflow.