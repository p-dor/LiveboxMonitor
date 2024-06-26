#!/usr/bin/env python

from setuptools import setup, find_packages

from LiveboxMonitor import (
    __title__,
    __description__,
    __url__,
    __version__,
    __build__,
    __author__,
    __author_email__,
    __license__,
    __copyright__
)

dependencies = [
    'PyQt6',
    'requests',
    'python-dateutil',
    'cryptography',
    'pyqtgraph'
]
"""Required dependencies to run the application."""

setup(
    name=__title__,
    version=__version__,
    description=__description__,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    license=__license__,
    copyright=__copyright__,

    install_requires=dependencies,
    packages=find_packages(),
    package_data={
        'LiveboxMonitor': ['resources/icons/*.png']
    },

    entry_points={
        'console_scripts': [
            'LiveboxMonitor = LiveboxMonitor.__main__:main'
        ]
    }
)