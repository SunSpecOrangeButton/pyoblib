from setuptools import setup, find_packages

TESTS_REQUIRE = [
    'pytest',
    'pytest-cov'
]

EXTRAS_REQUIRE = {
    'doc': ['sphinx', 'sphinx_rtd_theme'],
    'test': TESTS_REQUIRE
}
EXTRAS_REQUIRE['all'] = sorted(set(sum(EXTRAS_REQUIRE.values(), [])))

INSTALL_REQUIRE = [
    'lxml==4.2.5',
    'six>=1.10.0',
    'enum_compat==0.0.2',
    'jsondiff==1.1.2',
    'validators==0.12.4'
]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]

setup(
    name='oblib',
    version='1.0.1',
    description='Orange Button Python Library',
    long_description=
    """
    The Orange Button Python Library, also called, pyoblib, 
    provides functions to interact and work with the SunSpec 
    Orange Button Taxonomy and provides capabilities that 
    simplify working with Orange Button data.

    Documentation: https://pyoblib.readthedocs.io/en/latest/
    
    Source code: https://github.com/SunSpecOrangeButton/pyoblib
    """,
    author='SunSpec Alliance',
    author_email='support@sunspec.org',

    packages=find_packages(),
    include_package_data=True,

    extras_require=EXTRAS_REQUIRE,
    install_requires=INSTALL_REQUIRE,
    license='Apache 2.0',
    classifiers=CLASSIFIERS,
)
