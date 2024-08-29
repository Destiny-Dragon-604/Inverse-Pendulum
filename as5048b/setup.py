#!/usr/bin/env python3

'''
This file is part of the as5048b library (https://github.com/ansarid/as5048b).
Copyright (C) 2022  Daniyal Ansari

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import setuptools
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

install_requires = [
                    'smbus2',
                   ]

setuptools.setup(
    name='as5048b',
    version='0.0.1',
    description='Python Library for the AS5048B Absolute Magnetic Rotary Encoder',
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    keywords=['AS5048B', 'magnetic encoder', 'rotary encoder',],
    url='https://github.com/ansarid/as5048b',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
