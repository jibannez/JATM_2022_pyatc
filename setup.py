# -*- coding: utf-8 -*-
#from distutils.core import setup
from setuptools import setup

setup(
    name='pyatc',
    version='0.1',
    author='Jorge Ibañez Gijón',
    author_email='jorge.ibannez@uam.es',
    packages=['pyatc'],
    zip_safe=False,
    license='LICENSE.txt',
    description='pyatc library',
    long_description=open('README.md').read(),
    install_requires=[
        "numpy >= 1.8.1",
        "matplotlib >= 1.4",
        "pandas >= 0.17.1",
        "lxml >= 4.1.1",
    ],
)
