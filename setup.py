#! /usr/bin/env python
#! coding: utf-8
# Copyright (C) 2017-2018 cmj<cmj@cmj.tw>. All right reserved.

from setuptools import setup, find_packages
from sisyphus import __VERSION__

setup(
	name				= 'pysisyphus',
	version				= __VERSION__,
	author				= 'cmj',
	author_email		= 'cmj.tw',
	packages			= find_packages(),
	install_requires	= ['setproctitle'],
	entry_points		= {
		'console_scripts': 'sisyphus = sisyphus:cli.run',
	},
)
