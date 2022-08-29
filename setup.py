#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(name='vectorial_ui',
      version='0.1',
      description='UI to run comet sumulations using a vectorial model.',
      author='Jacob Duffy',
      author_email='jod0007@auburn.edu',
      url='https://github.com/jduffy0121/VectorialUI',
      scripts=['bin/UICreator.py'],
     )