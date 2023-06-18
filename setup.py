# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import find_packages, setup

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='smalifuzz',
    version='0.1.0',
    description='Sample package for Python-Guide.org',
    long_description=readme,
    author='Tavani Mauro',
    author_email='metalcorpe@gmail.com',
    url='https://github.com/metalcorpe/smalifuzz',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

