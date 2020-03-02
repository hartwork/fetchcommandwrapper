#!/usr/bin/env python
# Copyright (C) 2010 Sebastian Pipping <sebastian@pipping.org>
# Licensed under GPL v3 or later

from setuptools import setup

import sys
sys.path.insert(0, 'modules')
from fetchcommandwrapper.version import VERSION_STR

setup(
    name='fetchcommandwrapper',
    description='Wrapper around Aria2 for portage\'s FETCHCOMMAND variable',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='GPL v3 or later',
    version=VERSION_STR,
    url='https://github.com/hartwork/fetchcommandwrapper',
    author='Sebastian Pipping',
    author_email='sping@gentoo.org',
    setup_requires=[
        'setuptools>=38.6.0',  # for long_description_content_type
    ],
    package_dir={'':'modules', },
    packages=['fetchcommandwrapper', ],
    scripts=['fetchcommandwrapper', ],
    data_files=[
        ('share/fetchcommandwrapper', [
            'make.conf',
        ]),
    ],
)
