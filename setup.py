#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Caliope_Odisea Setup
    ~~~~~~~~~~~~~~

    :author: Sebastián Ortiz <neoecos@gmail.com>
    :copyright: (c) 2013 por Fundación CorreLibre
    :license:  GNU AFFERO GENERAL PUBLIC LICENSE

    Caliope Storage is the base of Caliope's Framework
    Copyright (C) 2013  Fundación Correlibre

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from setuptools import setup

setup(
    name='SIIM2_Server',
    version='0.0.1',
    package_dir={'': 'src'},
    packages=['cid', 'test'],
    license='GNU AFFERO GENERAL PUBLIC LICENSE',
    long_description=open('README.md').read(),
    author='Sebastián Ortiz Vásquez',
    author_email='neoecos@gmail.com',
    url='https://proyectos.correlibre.org/caliope/caliope_server_el_cid',
    install_requires=['Caliope-Odisea==0.0.3'],
    test_suite='nose.collector',
)
