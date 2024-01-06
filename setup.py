#!/usr/bin/env python3
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name="nativemessaging-ng",
      version="1.1.0",
      description="A package with basic native messaging apis for webextensions",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/roelderickx/nativemessaging-ng",
      author="Rayquaza01, roelderickx",
      author_email="nativemessaging-ng.pypi@derickx.be",
      license="MPL 2.0",
      packages=["nativemessaging"],
      entry_points={
          "console_scripts": ["nativemessaging-install = nativemessaging.install:main"]
      },
      include_package_data=True,
      package_data={"": ["README.md"]},
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
          "Operating System :: OS Independent"
      ])
