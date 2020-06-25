#!/usr/bin/env python
from setuptools import setup

setup(
    name="accuweather",
    version="0.0.6",
    author="Maciej Bieniek",
    author_email="maciej.bieniek@gmail.com",
    description="Python wrapper for getting weather data from AccuWeather servers.",
    include_package_data=True,
    url="https://github.com/bieniu/accuweather",
    license="Apache 2",
    packages=["accuweather"],
    python_requires=">=3.6",
    install_requires=["aiohttp"],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ],
    setup_requires=("pytest-runner"),
    tests_require=(
        "asynctest",
        "pytest-cov",
        "pytest-asyncio",
        "pytest-trio",
        "pytest-tornasync",
    ),
)
