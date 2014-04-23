from setuptools import setup, find_packages

setup(
    name = "dcp",
    version = "0.1",
    packages = find_packages(),
    author = "Chris Barrett",
    author_email = "chris.d.barrett@me.com",
    description = "Format a drive for use as a Digital Cinema Package.",
    license = "BSD3",
    entry_points = {'console_scripts': ['dcp = dcp.dcp:main',]}
)
