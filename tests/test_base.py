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
INVALID_API_KEY = "abcdef"
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
        assert isinstance(current_conditions["HasPrecipitation"], bool)
        assert not current_conditions["HasPrecipitation"]
        assert not current_conditions["PrecipitationType"]
        assert current_conditions["Temperature"]["Metric"]["Value"] == 23.1
        assert current_conditions["Temperature"]["Metric"]["Unit"] == "C"
        assert current_conditions["Temperature"]["Imperial"]["Value"] == 74
        assert current_conditions["Temperature"]["Imperial"]["Unit"] == "F"


@pytest.mark.asyncio
async def test_get_forecast():
    """Test with valid forecast data."""
    with open("tests/data/forecast_data.json") as file:
        forecast_data = json.load(file)

    with patch("accuweather.AccuWeather._async_get_data", return_value=forecast_data):
        async with ClientSession() as websession:
            accuweather = AccuWeather(
                VALID_API_KEY, websession, location_key=LOCATION_KEY
            )
            forecast = await accuweather.async_get_forecast()

        assert forecast["DailyForecasts"][0]["IconDay"] == 15
        assert forecast["DailyForecasts"][0]["PrecipitationProbabilityDay"] == 57
        assert forecast["DailyForecasts"][0]["WindDay"]["Speed"]["Value"] == 13.0
        assert forecast["DailyForecasts"][0]["TemperatureMax"]["Value"] == 24.8
        assert forecast["DailyForecasts"][0]["TemperatureMax"]["Unit"] == "C"
        assert forecast["DailyForecasts"][0]["AirQuality"]["Value"] == 23
        assert forecast["DailyForecasts"][0]["AirQuality"]["Type"] == "Ozone"


@pytest.mark.asyncio
async def test_invalid_api_key():
    """Test with invalid API key."""
    async with ClientSession() as websession:
        try:
            AccuWeather(
                INVALID_API_KEY, websession, latitude=LATITUDE, longitude=LONGITUDE
            )
        except InvalidApiKeyError as error:
            assert (
                str(error.status)
                == "Your API Key must be a 32-character hexadecimal string"
            )


@pytest.mark.asyncio
async def test_invalid_coordinates_1():
    """Test with invalid coordinates."""
    async with ClientSession() as websession:
        try:
            AccuWeather(VALID_API_KEY, websession, latitude=55.55, longitude="78.00")
        except InvalidCoordinatesError as error:
            assert str(error.status) == "Your coordinates are invalid"


@pytest.mark.asyncio
async def test_invalid_coordinates_2():
    """Test with invalid coordinates."""
    async with ClientSession() as websession:
        try:
            AccuWeather(VALID_API_KEY, websession, latitude=199.99, longitude=90.0)
        except InvalidCoordinatesError as error:
            assert str(error.status) == "Your coordinates are invalid"


@pytest.mark.asyncio
async def test_api_error():
    """Test with API error"""
    with patch(
        "accuweather.AccuWeather._async_get_data",
        side_effect=ApiError("Invalid response from AccuWeather API: 404"),
    ):
        async with ClientSession() as websession:
            try:
                accuweather = AccuWeather(
                    VALID_API_KEY, websession, latitude=LATITUDE, longitude=LONGITUDE
                )
                await accuweather.async_get_location()
            except ApiError as error:
                assert str(error.status) == "Invalid response from AccuWeather API: 404"


@pytest.mark.asyncio
async def test_requests_exceeded_error():
    """Test with requests exceeded error"""
    with patch(
        "accuweather.AccuWeather._async_get_data",
        side_effect=RequestsExceededError(
            "The allowed number of requests has been exceeded"
        ),
    ):
        async with ClientSession() as websession:
            try:
                accuweather = AccuWeather(
                    VALID_API_KEY, websession, latitude=LATITUDE, longitude=LONGITUDE
                )
                await accuweather.async_get_location()
            except RequestsExceededError as error:
                assert (
                    str(error.status)
                    == "The allowed number of requests has been exceeded"
                )
