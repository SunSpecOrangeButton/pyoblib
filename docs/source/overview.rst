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


Requirements
============
- Python 2.7, 3.4-3.6


Installation
============

A series of Bash (Mac/Linux) shell scripts are available to assist with development and packaging.
Their state is preliminary but they can be used to get started.

* cli.sh: Runs the CLI before it is packaged.
* dist-cli.sh: Packages the CLI into a single file executable.
* docs.sh: Creates the documentation (currently requires some manual work).
* setup-dev.sh: Downloads the solar-taxonomy, us-gaap taxonomy, and Units registry.
* tests.sh Runs the python tests.
* tests-cli.sh Runs the CLI test suite.

All scripts must be run from the root directory (i.e. "scripts/tests.sh" is the correct usage).
Run "scripts/setup-dev.sh" before usage of other scripts.

Usage on Windows is a future feature (contributions are welcome!). It should be possible to use on Windows with
manual setup at this point in time.

Running the Tests
-----------------

In order to run the tests run the following scripts:

* tests.sh - Runs the python tests.
* tests-cli.sh - Runs the CLI test suite.

