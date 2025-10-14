#!/usr/bin/env python3
# Copyright (C) 2010 Sebastian Pipping <sebastian@pipping.org>
# Licensed under GPL v3 or later

import sys

from setuptools import find_packages, setup

sys.path.insert(0, "modules")
from fetchcommandwrapper.version import VERSION_STR

setup(
    name="fetchcommandwrapper",
    description="Wrapper around Aria2 for portage's FETCHCOMMAND variable",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="GPL v3 or later",
    version=VERSION_STR,
    url="https://github.com/hartwork/fetchcommandwrapper",
    author="Sebastian Pipping",
    author_email="sping@gentoo.org",
    python_requires=">=3.10",
    setup_requires=[
        "setuptools>=38.6.0",  # for long_description_content_type
    ],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "fetchcommandwrapper = fetchcommandwrapper.__main__:main",
        ],
    },
    data_files=[
        (
            "share/fetchcommandwrapper",
            [
                "make.conf",
            ],
        ),
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet",
        "Topic :: Internet :: File Transfer Protocol (FTP)",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
