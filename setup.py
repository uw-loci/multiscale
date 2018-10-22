# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE.txt') as f:
    license = f.read()

setup(
    name='mp_img_manip',
    version='0.1.0',
    author='Michael Pinkert',
    author_email='mpinkert@wisc.edu',
    description='An multiscale image processing library for the Laboratory of Optical and Computational Instrumentation',
    long_description=readme,
    url='https://github.com/uw-loci/multiscale_imaging',
    license=license,
    packages=find_packages()
)

