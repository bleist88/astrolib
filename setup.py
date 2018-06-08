
from setuptools import setup

setup(
    name                = "astrolib",
    version             = "6.2831853",
    description         = "a library of astronomy related packages",
    long_description    = open("README.md").read(),
    author              = "Brian Leist",
    author_email        = "bleist@protonmail.com",
    url                 = "https://github.com/bleist88/astrolib",
    license             = open("LICENSE").read(),
    zip_safe            = True,
    packages            = [
        "astrolib/io", "astrolib/mcc", "astrolib/photometry"
    ],
    scripts             = [
        "astrolib/scripts/mcc", "astrolib/scripts/pysex"
    ],
)
