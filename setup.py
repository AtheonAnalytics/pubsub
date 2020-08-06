#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools
from setuptools import setup

requirements = [
    'kombu>=4, <6',
    'celery>=4, <5',
]
setup_requirements = [
]

test_requirements = [
]

extras_require = {
    'django': ["django"],
    'flask': ['flask']
}

setup(
    author="Samuel Luen-English",
    author_email='sam.luenenglish@atheon.co.uk',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Publish and Subscribe utilities",
    install_requires=requirements,
    extras_require=extras_require,
    include_package_data=True,
    keywords='pubsub',
    name='pubsub',
    packages=setuptools.find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    version='0.0.2',
)
