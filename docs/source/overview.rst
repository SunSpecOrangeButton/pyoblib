==========
 Overview
==========

The Orange Button Python Library, also called, pyoblib, provides functions to interact and work with the
SunSpec Orange Button Taxonomy and provides capabilities that simplify working with Orange Button data.

This project is being actively developed and is not yet ready for production use.

The pyoblib library leverages the Python standard library to the extent possible to minimize required dependencies.
pyoblib is Open Sourced and is maintained by the Orange Button Open Source community. The source code is available on GitHub -
`pyoblib <https://github.com/SunSpecOrangeButton/pyoblib>`_.
The code is licensed under Apache 2.0.

The SunSpec Orange Button Taxonomy is also published as open source on GitHub -
`solar-taxonomy <https://github.com/SunSpecOrangeButton/solar-taxonomy>`_.


Features
========
- Includes an in-memory data model
- Includes in-memory meta-data about the SunSpec Orange Button Taxonomy
- Provides support for XML/JSON input-output
- Provides support for data conversion and data validation
- Supports identifier generation and validation


pyoblib Class and Module Structure
==================================
.. figure:: pyoblib.png
   :scale: 75 %
   :alt: pyoblib module structure


Requirements
============
- Python 2.7, 3.4-3.6


Installation
============

Installing the library from PyPI
--------------------------------

To install the library from the Python Package Index (PyPI), run the following command::

    pip install oblib

Installing the library from GitHub
----------------------------------

Follow the steps outlined below to install the library for development from GitHub.

1. Create a fork of the `pyoblib <https://github.com/SunSpecOrangeButton/pyoblib>`_ GitHub repository.
2. Clone it locally.
3. Navigate to the pyoblib root directory - ``cd pyoblib``
4. Run the setup script - ``scripts/setup-dev.sh``
5. Install using setup.py - ``python setup.py install``

A series of Bash (Mac/Linux) shell scripts are available to assist with development and packaging.

* cli.sh: Runs the CLI before it is packaged.
* dist-cli.sh: Packages the CLI into a single executable file.
* setup-dev.sh: Downloads the solar-taxonomy, us-gaap taxonomy, and Units registry.
* tests.sh: Runs the python tests.
* tests-cli.sh: Runs the CLI test suite.

All scripts must be run from the root directory (i.e. ``scripts/tests.sh`` is the correct usage).
Run ``scripts/setup-dev.sh`` before usage of other scripts.


Running the Tests
~~~~~~~~~~~~~~~~~

In order to run the tests run the following scripts:

* tests.sh - Runs the python tests.
* tests-cli.sh - Runs the CLI test suite.

Installing the CLI Tool
-----------------------

Follow the steps outlined below to the Command Line Interface (CLI) tool.

1. Download an executable that matches your system type -

    • Mac - :download:`OB Mac Executable <../../dist-cli/Mac/ob>`
    • Windows - :download:`OB Windows Executable <../../dist-cli/Windows/ob.exe>`
    • Linux - :download:`OB Linux Executable <../../dist-cli/Linux/ob>`

2. Register the executable -

To be able to run the executable from the command line, follow one of the two options -
    a. Move the downloaded file to the executable path -
        • Mac, Linux - ``sudo mv ob /usr/local/bin``
    b. Or, add the OB executable file path to the system PATH environment variable.

Now, the CLI tool can be invoked from the command line by using the command ``ob``.
For the full set of commands, use the help option as ``ob --help``
