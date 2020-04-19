# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='odmadmpy',
    version='0.1.0',
    description='A quick and dirty writer for CCSDS and CIC Orbit and Attitude Data Messages',
    long_description=readme,
    author='Clément Jonglez',
    author_email='clement@jonglez.space',
    url='https://github.com/GorgiAstro/ccsds-cic-odm-adm-py',
    license=license,
    packages=find_packages(exclude=('samples', 'docs', 'generated-ccsds-cic'))
)
