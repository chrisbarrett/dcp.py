"""Project configuration for setuptools.
"""

from setuptools import setup, find_packages
import dcp.dcp as package

setup(
    name            = "dcp",
    version         = package.VERSION,
    packages        = find_packages(),
    author          = "Chris Barrett",
    author_email    = "chris.d.barrett@me.com",
    url             = 'https://github.com/chrisbarrett/dcp.py',
    description     = "Format a drive for use as a Digital Cinema Package.",
    license         = "BSD2",
    entry_points    = {
        'console_scripts': ['dcp = dcp.dcp:main',]
    }
)
