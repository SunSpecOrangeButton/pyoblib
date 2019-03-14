# Introduction

Thank you for considering contributing to pyoblib. It's people like you that make pyoblib such a great library.

There are many ways in which you can contribute. A contribution may be
* writing code which can be incorporated into pyoblib
* improving the documentation
* submitting bug reports and feature requests

# Ground Rules

pyoblib contains core source code that may be used by other Orange Button code.  By definition, the functionality in
this library should be consumable by multiple other Orange Button projects.  If the functionality is only usable in a
single instance it should be placed in another project.

Source code in Orange Button Core must:

* Be fully commented
* Contain comprehensive test coverage
* Subject to vulnerability scan

# Getting started

You must sign the SunSpec Contributor License Agreement before enhancing the source code or the documentation.
Please see the instructions on how to submit a signed CLA on the [Orange Button Open Source Community web page](https://sunspec.org/ob-open-source-community/).

Also, please email support@sunspec.org or post a message on the [Orange Button Slack Channel](https://orange-button.slack.com/)
so we are aware of your intent to contribute.

For all changes follow the procedure documented at the bottom of the
[Orange Button Open Source Community web page](https://sunspec.org/ob-open-source-community/).

## Your First Contribution

Unsure where to begin?  Please enquire on our [Slack Channel](https://orange-button.slack.com/).

### Writing tests

All public member functions should have a corresponding test located in a test file in oblib/tests with "test_" being
prefixed before the function name.  Whenever a new function or method is written please write a test.  Also whenever an
issue is identified add additional tests so that the issue can be fixed and the issue will not re-occur.  Private member
function tests are optional although in some cases they may be needed to fix issues.

The CLI tests only test that the CLI completes and returns exit status 0 (success).  The CLI tests do not test the
functionality of the CLI.  This should be sufficient since the functionality is already covered in the Python Test cases.

### Code style

The project style guide is [PEP8](https://www.python.org/dev/peps/pep-0008/).  Flake8 is a useful tool to test whether
the PEP8 standard has been met (although this testing has not been automated yet).

Another useful resource is the [Google Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md) which
has additional details about writing coding above and beyond what is available in pep8.

## How to report a bug

Please use [GitHub Issues](https://github.com/SunSpecOrangeButton/pyoblib/issues) for all bug reports.
If you find a security vulnerability, do NOT open an issue. Email support@sunspec.org instead.

## How to suggest a feature or enhancement

Please use the [Orange Button Slack Channel](https://orange-button.slack.com/) to suggest features and enhancements.

# Code review process

All code is subject to a peer review.  When a pull request is submitted at least one person with collaboration status
must review the code before merging. All necessary checks (CLA verification, TravisCI) must pass before a pull request
is merged.

# Code of Conduct

Being a library programmed in Python the [Python Community Code of Conduct](https://www.python.org/psf/codeofconduct/) is followed.
  
# Community

The [Orange Button Slack Channel](https://orange-button.slack.com/) is the best online resource for discussions
regarding pyoblib. You are also invited to join regular developer meetings that occur (just ask to be invited on the
Slack Channel).