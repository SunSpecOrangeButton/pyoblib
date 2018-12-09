# Orange Button Python Library (pyoblib)

The Orange Button Python library contains core source code that may be used by other Orange Button code.  By definition functionality in this library should be consumable by multiple other Orange Button projects.  If functionality is only usable in a single instance it should be placed in another project.

Full Documentation can be found at [Read the Docs](https://pyoblib.readthedocs.io/en/latest/).

NOTE: At this point in time the Core library is being setup and is in development.  It may be possible to use some of its functionality although it is likely to see significant regular changes in SDK signatures.

## Getting Started

### Requirements

Python 2.7, 3.4 - 3.6.  The recommended version is Python 3.6.

### Installation

A series of Bash (Mac/Linux) shell scripts are available to assist with development and packaging. Their state is preliminary but they can be used to get started.

* cli.sh: Runs the CLI before it is packaged.
* dist-cli.sh: Packages the CLI into a single file executable.
* docs.sh: Creates the documentation (currently requires some manual work).
* setup-dev.sh: Downloads the solar-taxonomy, us-gaap taxonomy, and Units registry.
* tests.sh Runs the python tests.
* tests-cli.sh Runs the CLI test suite.

All scripts must be run from the root core directory (i.e. "scripts/tests.sh" is the correct usage).  Run "scripts/setup-dev.sh" before usage of other scripts.

Usage on Windows is a future feature (feel free to add).  It should be possible to use on Windows with manual setup at this point in time.

Long Term this project is being updated so that its procedures mimic the successful [pvlib](https://github.com/pvlib/pvlib-python) project.  This way many of the configuration files and lessons learned by the pvlib team can be levereaged.  At this point in time many of the scripts listed above may no longer be necessary and may be deprecated.

## Running the tests

In order to run the tests run:

* tests.sh Runs the python tests.
* tests-cli.sh Runs the CLI test suite.

Upon a pull request Travis will also operate all of the test cases.

### Break down into end to end tests

All public member functions should have a corresponding test located in a test file in oblib/tests with "test_" being prefixed before the function name.  Whenever a new function or method is written please write a test.  Also whenever an issue is identified add additional tests so that the issue can be fixed and the issue will not re-occur.  Private member function tests are optional although in some cases they may be needed to fix issues.

The CLI tests only test that the CLI completes and returns exit status 0 (success).  The CLI tests do not test the functionality of the CLI.  This should be sufficient since the functionality is already covered in the Python Test cases.

### And coding style tests

The project style guide is [PEP8](https://www.python.org/dev/peps/pep-0008/).  Flake8 is a useful tool to test whether the PEP8 standard has been met (although this has not been automated, nor has a flake8 configuration file been established yet).

Another useful resource is the [Google Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md) which has additional details about writing coding above and beyond what is available in pep8.

## Deployment

The future intent is to deploy to PyPl.  This is not implemented yet.  PyInstaller is used to build a working CLI.

## Built With

Other than Python and several Python libraries there is no frameworks in use by design.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

Versioning will be established when this reaches its first release.  At this point in time this is a development release.

## Authors

See the list of [contributors](https://github.com/SunSpecOrangeButton/pyoblib/graphs/contributors) who participated in this project.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* The Orange Button Specification was built by several organizations in the [Orange Button Implementors Network](https://sunspec.org/thank-signing-orange-button-implementor/) with guidance by [XBRL US](https://xbrl.us/home/about/).
* Orange Button GitHub and tool accounts are supplied by [Sunspec Alliance](https://sunspec.org/sunspec-about/).
* The procedures and infrastructure for this library are based upon pvlib.  For more information see William F. Holmgren, Clifford W. Hansen, and Mark A. Mikofski. "pvlib python: a python package for modeling solar energy systems." Journal of Open Source Software, 3(29), 884, (2018). [https://doi.org/10.21105/joss.00884](https://doi.org/10.21105/joss.00884)


