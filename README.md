# Orange Button Python Library (pyoblib)

The Orange Button Python library contains core source code that may be used by other Orange Button code.  By definition functionality in this library should be consumable by multiple other Orange Button projects.  If functionality is only usable in a single instance it should be placed in another project.

Documentation (API interface) is here: [link](https://github.com/SunSpecOrangeButton/pyoblib/tree/master/docs)


NOTE: At this point in time the Core library is being setup and is in development.  It may be possible to use some of its functionality although it is likely to see significant regular changes in SDK signatures.

The rest of this read me file is in template form at this point in time.  It will be updated in the near future.

## Getting Started

Temporary Instructions:

A series of shell scripts are availalable to assist with development, packaging, etc...   Their state is preliminary but they can be used to get started.

* cli.sh: Runs the CLI before it is packaged.
* dist-cli.sh: Packages the CLI into a single file executable.
* docs.sh: Creates the documentation (currently requires some manual work).
* setup-dev.sh: Downloads the solar-taxonomy, us-gaap taxonomy, and Units registry.
* tests-cli.sh Runs the CLI test suite.
* tests.sh Runs the python tests.

All scripts must be run from the root core directory (i.e. "scripts/tests.sh" is the correct usage).  Run "scripts/setup-dev.sh" before usage of other scripts.

Long Term this project is being updated so that its procedures mimic the successful [pvlib](https://github.com/pvlib/pvlib-python) project.  This way many of the configuration files and lessons learned by the pvlib team can be levereaged.  At this point in time many of the scripts listed above
may no longer be necessary and may be deprecated.

### NOTE: THE REST OF THIS FILE IS STILL IN THE FORMAT OF THE TEMPLATE

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

For the versions available, see the [releases on this repository](https://github.com/SunSpecOrangeButton/template-application/releases).

## Authors

* **Author Name** - *Initial work* - [GitHubUser](https://github.com/GitHubUserLink)

See also the list of [contributors](https://github.com/SunSpecOrangeButton/template-application/contributors) who participated in this project.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

