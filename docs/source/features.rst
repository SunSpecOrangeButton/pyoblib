Features
========

pyoblib has capabilities for working with:

* identifiers
* taxonomy

Identifier Design
-----------------

Identifier is a single module that allows generation and validation of Orange Button Identifiers
(currently UUID's).

Taxonomy Design
---------------

Taxonomy returns an in memory representation of the Solar Taxonomy XSD (available at
`solar-taxonomy <https://github.com/SunSpecOrangeButton/solar-taxonomy>`_ ).


.. figure:: taxonomy.png
   :scale: 75 %
   :alt: taxonomy structure

Usage
=====

A series of shell scripts are available to assist with development, packaging, etc....   Their state is preliminary but they can be used to get started.

* cli.sh: Runs the CLI before it is packaged.
* dist-cli.sh: Packages the CLI into a single file executable.
* docs.sh: Creates the documentation (currently requires some manual work).
* setup-dev.sh: Downloads the solar-taxonomy, us-gaap taxonomy, and Units registry.
* tests-cli.sh Runs the CLI test suite.
* tests.sh Runs the python tests.

All scripts must be run from the root core directory (i.e. "scripts/tests.sh" is the correct usage).  Run "scripts/setup-dev.sh" before usage of other scripts.
