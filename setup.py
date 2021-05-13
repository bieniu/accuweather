#!/usr/bin/env python
from setuptools import find_packages, setup

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="accuweather",
    version="0.2.0",
    author="Maciej Bieniek",
    description="Python wrapper for getting weather data from AccuWeather servers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    url="https://github.com/bieniu/accuweather",
    license="Apache-2.0 License",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.6",
    install_requires=list(val.strip() for val in open("requirements.txt")),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    setup_requires=("pytest-runner"),
    tests_require=list(val.strip() for val in open("requirements-test.txt")),
)
