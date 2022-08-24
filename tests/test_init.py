"""Tests for accuweather package."""
import json
from http import HTTPStatus

import aiohttp
import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from accuweather import (
    AccuWeather,
    ApiError,
    InvalidApiKeyError,
    InvalidCoordinatesError,
    RequestsExceededError,
)

HEADERS = {"RateLimit-Remaining": "23"}
INVALID_API_KEY = "abcdef"
LATITUDE = 52.0677904
LOCATION_KEY = "268068"
LONGITUDE = 19.4795644
VALID_API_KEY = "32-character-string-1234567890qw"


@pytest.mark.asyncio
async def test_get_location():
    """Test with valid location data."""
    with open("tests/fixtures/location_data.json", encoding="utf-8") as file:
        location_data = json.load(file)

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        # pylint:disable=line-too-long
        session_mock.get(
            "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=32-character-string-1234567890qw&q=52.0677904%252C19.4795644",
            payload=location_data,
            headers=HEADERS,
        )
        accuweather = AccuWeather(
            VALID_API_KEY, session, latitude=LATITUDE, longitude=LONGITUDE
        )
        await accuweather.async_get_location()

    await session.close()

    assert accuweather.location_name == "Piątek"
    assert accuweather.location_key == "268068"
    assert accuweather.requests_remaining == 23


@pytest.mark.asyncio
async def test_get_current_conditions():
    """Test with valid current condition data."""
    with open("tests/fixtures/current_condition_data.json", encoding="utf-8") as file:
        current_condition_data = json.load(file)
    with open("tests/fixtures/location_data.json", encoding="utf-8") as file:
        location_data = json.load(file)

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        # pylint:disable=line-too-long
        session_mock.get(
            "https://dataservice.accuweather.com/currentconditions/v1/268068?apikey=32-character-string-1234567890qw&details=true",
            payload=current_condition_data,
            headers=HEADERS,
        )
        session_mock.get(
            "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=32-character-string-1234567890qw&q=52.0677904%252C19.4795644",
            payload=location_data,
            headers=HEADERS,
        )
        accuweather = AccuWeather(
            VALID_API_KEY, session, latitude=LATITUDE, longitude=LONGITUDE
        )
        current_conditions = await accuweather.async_get_current_conditions()

    await session.close()

    assert current_conditions["WeatherIcon"] == 7
    assert isinstance(current_conditions["HasPrecipitation"], bool)
    assert not current_conditions["HasPrecipitation"]
    assert not current_conditions["PrecipitationType"]
    assert current_conditions["Temperature"]["Metric"]["Value"] == 23.1
    assert current_conditions["Temperature"]["Metric"]["Unit"] == "C"
    assert current_conditions["Temperature"]["Imperial"]["Value"] == 74
    assert current_conditions["Temperature"]["Imperial"]["Unit"] == "F"
    assert accuweather.requests_remaining == 23


@pytest.mark.asyncio
async def test_get_forecast():
    """Test with valid forecast data."""
    with open("tests/fixtures/forecast_data.json", encoding="utf-8") as file:
        forecast_data = json.load(file)
    with open("tests/fixtures/location_data.json", encoding="utf-8") as file:
        location_data = json.load(file)

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        # pylint:disable=line-too-long
        session_mock.get(
            "https://dataservice.accuweather.com/forecasts/v1/daily/5day/268068?apikey=32-character-string-1234567890qw&details=true&metric=True",
            payload=forecast_data,
            headers=HEADERS,
        )
        session_mock.get(
            "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=32-character-string-1234567890qw&q=52.0677904%252C19.4795644",
            payload=location_data,
            headers=HEADERS,
        )

        accuweather = AccuWeather(
            VALID_API_KEY, session, latitude=LATITUDE, longitude=LONGITUDE
        )
        forecast = await accuweather.async_get_forecast()

    await session.close()

    assert forecast[0]["IconDay"] == 15
    assert forecast[0]["PrecipitationProbabilityDay"] == 57
    assert forecast[0]["WindDay"]["Speed"]["Value"] == 13.0
    assert forecast[0]["TemperatureMax"]["Value"] == 24.8
    assert forecast[0]["TemperatureMax"]["Unit"] == "C"
    assert forecast[0]["Ozone"]["Value"] == 23
    assert accuweather.requests_remaining == 23


@pytest.mark.asyncio
async def test_get_hourly_forecast():
    """Test with valid hourly_forecast data."""
    with open("tests/fixtures/hourly_forecast_data.json", encoding="utf-8") as file:
        hourly_forecast_data = json.load(file)
    with open("tests/fixtures/location_data.json", encoding="utf-8") as file:
        location_data = json.load(file)

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        # pylint:disable=line-too-long
        session_mock.get(
            "https://dataservice.accuweather.com/forecasts/v1/hourly/12hour/268068?apikey=32-character-string-1234567890qw&details=true&metric=True",
            payload=hourly_forecast_data,
            headers=HEADERS,
        )
        session_mock.get(
            "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=32-character-string-1234567890qw&q=52.0677904%252C19.4795644",
            payload=location_data,
            headers=HEADERS,
        )

        accuweather = AccuWeather(
            VALID_API_KEY, session, latitude=LATITUDE, longitude=LONGITUDE
        )
        forecast = await accuweather.async_get_forecast_hourly()

    await session.close()

    assert forecast[0]["WeatherIcon"] == 4
    assert forecast[0]["HasPrecipitation"] is False
    assert forecast[0]["UVIndex"] == 2
    assert forecast[0]["Temperature"]["Value"] == 26.3
    assert forecast[0]["Temperature"]["Unit"] == "C"
    assert accuweather.requests_remaining == 23


@pytest.mark.asyncio
async def test_invalid_api_key_1():
    """Test with invalid API key."""
    async with ClientSession() as session:
        try:
            AccuWeather(
                INVALID_API_KEY, session, latitude=LATITUDE, longitude=LONGITUDE
            )
        except InvalidApiKeyError as error:
            assert (
                str(error.status)
                == "Your API Key must be a 32-character hexadecimal string"
            )


@pytest.mark.asyncio
async def test_invalid_api_key_2():
    """Test with invalid API key."""
    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        # pylint:disable=line-too-long
        session_mock.get(
            "https://dataservice.accuweather.com/currentconditions/v1/268068?apikey=32-character-string-1234567890qw&details=true",
            status=HTTPStatus.UNAUTHORIZED.value,
        )
        accuweather = AccuWeather(VALID_API_KEY, session, location_key=LOCATION_KEY)
        try:
            await accuweather.async_get_current_conditions()
        except InvalidApiKeyError as error:
            assert str(error.status) == "Invalid API key"

    await session.close()


@pytest.mark.asyncio
async def test_invalid_coordinates_1():
    """Test with invalid coordinates."""
    async with ClientSession() as session:
        try:
            AccuWeather(VALID_API_KEY, session, latitude=55.55, longitude="78.00")
        except InvalidCoordinatesError as error:
            assert str(error.status) == "Your coordinates are invalid"


@pytest.mark.asyncio
async def test_invalid_coordinates_2():
    """Test with invalid coordinates."""
    async with ClientSession() as session:
        try:
            AccuWeather(VALID_API_KEY, session, latitude=199.99, longitude=90.0)
        except InvalidCoordinatesError as error:
            assert str(error.status) == "Your coordinates are invalid"


@pytest.mark.asyncio
async def test_api_error():
    """Test with API error."""
    payload = {
        "Code": "ServiceError",
        "Message": "API error.",
    }

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        # pylint:disable=line-too-long
        session_mock.get(
            "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=32-character-string-1234567890qw&q=52.0677904%252C19.4795644",
            payload=payload,
            status=404,
        )
        accuweather = AccuWeather(
            VALID_API_KEY, session, latitude=LATITUDE, longitude=LONGITUDE
        )
        try:
            await accuweather.async_get_location()
        except ApiError as error:
            assert str(error.status) == "Invalid response from AccuWeather API: 404"

    await session.close()


@pytest.mark.asyncio
async def test_requests_exceeded_error():
    """Test with requests exceeded error."""
    payload = {
        "Code": "ServiceUnavailable",
        "Message": "The allowed number of requests has been exceeded.",
    }

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        # pylint:disable=line-too-long
        session_mock.get(
            "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=32-character-string-1234567890qw&q=52.0677904%252C19.4795644",
            payload=payload,
            status=503,
        )
        accuweather = AccuWeather(
            VALID_API_KEY, session, latitude=LATITUDE, longitude=LONGITUDE
        )
        try:
            await accuweather.async_get_location()
        except RequestsExceededError as error:
            assert (
                str(error.status) == "The allowed number of requests has been exceeded"
            )

    await session.close()
