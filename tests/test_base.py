"""Tests for accuweather package."""
import json

from accuweather import (
    AccuWeather,
    ApiError,
    InvalidApiKeyError,
    InvalidCoordinatesError,
    RequestsExceededError,
)
from aiohttp import ClientSession
from asynctest import patch
import pytest

VALID_API_KEY = "32-character-string-1234567890qw"
LATITUDE = 52.0677904
LONGITUDE = 19.4795644
LOCATION_KEY = "268068"


@pytest.mark.asyncio
async def test_get_location():
    """Test with valid location data."""
    with open("tests/data/location_data.json") as file:
        location_data = json.load(file)

    with patch("accuweather.AccuWeather._async_get_data", return_value=location_data):
        async with ClientSession() as websession:
            accuweather = AccuWeather(
                VALID_API_KEY, websession, latitude=LATITUDE, longitude=LONGITUDE
            )
            await accuweather.async_get_location()

        assert accuweather.location_name == "Piątek"
        assert accuweather.location_key == "268068"


@pytest.mark.asyncio
async def test_get_current_conditions():
    """Test with valid current condition data."""
    with open("tests/data/current_condition_data.json") as file:
        current_condition_data = json.load(file)

    with patch(
        "accuweather.AccuWeather._async_get_data", return_value=current_condition_data
    ):
        async with ClientSession() as websession:
            accuweather = AccuWeather(
                VALID_API_KEY, websession, location_key=LOCATION_KEY
            )
            current_conditions = await accuweather.async_get_current_conditions()

        assert current_conditions["WeatherIcon"] == 7
        assert current_conditions["HasPrecipitation"] == False
        assert current_conditions["PrecipitationType"] == None
        assert current_conditions["Temperature"]["Metric"]["Value"] == 23.1
        assert current_conditions["Temperature"]["Metric"]["Unit"] == "C"
        assert current_conditions["Temperature"]["Imperial"]["Value"] == 74
        assert current_conditions["Temperature"]["Imperial"]["Unit"] == "F"
