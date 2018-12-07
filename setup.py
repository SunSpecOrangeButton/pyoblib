from setuptools import setup


TESTS_REQUIRE = ['pytest']
EXTRAS_REQUIRE = {
    'doc': ['sphinx', 'sphinx_rtd_theme'],
    'test': TESTS_REQUIRE
}
EXTRAS_REQUIRE['all'] = sorted(set(sum(EXTRAS_REQUIRE.values(), [])))

setup(
    name='pyoblib',
    version='0.1',
    description='Orange Button Python Library',
    long_description=
    """
    The Orange Button Python Library, also called, pyoblib, 
    provides functions to interact and work with the SunSpec 
    Orange Button Taxonomy and provides capabilities that 
    simplify working with Orange Button data. This project is 
    being actively developed and is not yet ready for production use.
    Documentation: https://pyoblib.readthedocs.io/en/latest/
    Source code: https://github.com/SunSpecOrangeButton/pyoblib
    """,
    author='SunSpec Alliance, GitHub Contributors',
    author_email='support@sunspec.org',
    packages=['oblib'],
    extras_require=EXTRAS_REQUIRE,
    license='Apache 2.0'
    )
