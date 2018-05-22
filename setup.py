# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE.txt') as f:
    license = f.read()

setup(
    name='mp_img_manip',
    version='0.1.0',
    description='An image processing library for the Laboratory of Optical and Computational Instrumentation',
    long_description=readme,
    author='Michael Pinkert',
    author_email='mpinkert@wisc.edu',
    url='https://github.com/uw-loci/mp-python-modules',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

