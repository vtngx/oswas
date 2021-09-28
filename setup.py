#!/usr/bin/env python

import setuptools

setuptools.setup(
  name='OSWAS',
  version='1.0.0',
  description='Optimized Solutions for Web App Scanners',
  author='',
  packages=setuptools.find_packages(),
  python_requires='>=3.6',
  install_requires=[],
  entry_points={
    'console_scripts': [
      'app = app.bin.app:main'
    ]
  }
)