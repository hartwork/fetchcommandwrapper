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
    license='GPL v3 or later',
    version=VERSION_STR,
    url='https://github.com/hartwork/fetchcommandwrapper',
    author='Sebastian Pipping',
    author_email='sping@gentoo.org',
    package_dir={'':'modules', },
    packages=['fetchcommandwrapper', ],
    scripts=['fetchcommandwrapper', ],
    data_files=[
        ('share/fetchcommandwrapper', [
            'make.conf',
        ]),
    ],
)
