"""Setup module for accuweather."""

from pathlib import Path

from setuptools import setup

PROJECT_DIR = Path(__file__).parent.resolve()
README_FILE = PROJECT_DIR / "README.md"
VERSION = "4.0.0"

setup(
    name="accuweather",
    version=VERSION,
    author="Maciej Bieniek",
    description="Python wrapper for getting weather data from AccuWeather API.",
    long_description=README_FILE.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    include_package_data=True,
    url="https://github.com/bieniu/accuweather",
    license="Apache-2.0",
    packages=["accuweather"],
    package_data={"accuweather": ["py.typed"]},
    python_requires=">=3.12",
    install_requires=["aiohttp>=3.9.4", "orjson"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3 :: Only",
        "Typing :: Typed",
    ],
)
