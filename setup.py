#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

exec(open("nativemessaging/version.py").read())

with open('README.md', 'r', encoding='utf-8') as fh:
    README = fh.read()

setuptools.setup(
    name="nativemessaging-ng",
    version=__version__,
    license=__license__,
    author=__author__,
    author_email="nativemessaging-ng.pypi@derickx.be",
    description="A package with basic native messaging apis for webextensions",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/roelderickx/nativemessaging-ng",
    packages=setuptools.find_packages(),
    python_requires='>=3.0',
    entry_points={
        "console_scripts": ["nativemessaging-install = nativemessaging.install:main"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent"
    ]
)
