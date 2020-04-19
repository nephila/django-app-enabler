#!/usr/bin/env python
# -*- coding: utf-8 -*-  # NOQA

import app_enabler
from setuptools import find_packages, setup

version = app_enabler.__version__

readme = open("README.rst").read()
history = open("HISTORY.rst").read().replace(".. :changelog:", "")

setup(
    name="app_enabler",
    version=version,
    description="Autoconfigurator for django applications",
    long_description=readme + "\n\n" + history,
    author="Iacopo Spalletti",
    author_email="i.spalletti@nephila.digital",
    url="https://www.nephila.digital",
    packages=find_packages(exclude=["test*"]),
    include_package_data=True,
    install_requires=["astor", "click"],
    license="BSD",
    zip_safe=False,
    keywords="",
    test_suite="cms_helper.run",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
