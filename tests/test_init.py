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

    assert current_conditions.weather_icon == 38
    assert current_conditions.precipitation_type is None
    assert current_conditions.temperature.value == 0.5
    assert current_conditions.temperature.unit == "°C"
    assert accuweather.requests_remaining == 23


@pytest.mark.asyncio
async def test_get_daily_forecast():
    """Test with valid forecast data."""
    with open("tests/fixtures/daily_forecast_data.json", encoding="utf-8") as file:
        daily_forecast_data = json.load(file)
    with open("tests/fixtures/location_data.json", encoding="utf-8") as file:
        location_data = json.load(file)

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(
            "https://dataservice.accuweather.com/forecasts/v1/daily/5day/268068?apikey=32-character-string-1234567890qw&details=true&metric=true",
            payload=daily_forecast_data,
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
        forecast = await accuweather.async_get_daily_forecast()

    await session.close()

    assert forecast[0].weather_icon_day == 7
    assert forecast[0].precipitation_probability_day.value == 25
    assert forecast[0].precipitation_probability_day.unit == "%"
    assert forecast[0].wind_speed_day.value == 22.2
    assert forecast[0].wind_speed_day.unit == "km/h"
    assert forecast[0].temperature_max.value == 16.1
    assert forecast[0].temperature_max.unit == "°C"
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
        session_mock.get(
            "https://dataservice.accuweather.com/forecasts/v1/hourly/12hour/268068?apikey=32-character-string-1234567890qw&details=true&metric=true",
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
        forecast = await accuweather.async_get_hourly_forecast()

    await session.close()

    assert forecast[0].weather_icon == 18
    assert forecast[0].uv_index.value == 1
    assert forecast[0].temperature.value == 11.7
    assert forecast[0].temperature.unit == "°C"
    assert accuweather.requests_remaining == 23


@pytest.mark.asyncio
async def test_invalid_api_key_1():
    """Test with invalid API key."""
    async with ClientSession() as session:
        with pytest.raises(
            InvalidApiKeyError,
            match="Your API Key must be a 32-character hexadecimal string",
        ):
            AccuWeather(
                INVALID_API_KEY, session, latitude=LATITUDE, longitude=LONGITUDE
            )


@pytest.mark.asyncio
async def test_invalid_api_key_2():
    """Test with invalid API key."""
    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(
            "https://dataservice.accuweather.com/currentconditions/v1/268068?apikey=32-character-string-1234567890qw&details=true",
            status=HTTPStatus.UNAUTHORIZED.value,
        )
        accuweather = AccuWeather(VALID_API_KEY, session, location_key=LOCATION_KEY)
        with pytest.raises(InvalidApiKeyError, match="Invalid API key"):
            await accuweather.async_get_current_conditions()

    await session.close()


@pytest.mark.asyncio
async def test_invalid_coordinates_1():
    """Test with invalid coordinates."""
    async with ClientSession() as session:
        with pytest.raises(
            InvalidCoordinatesError, match="Your coordinates are invalid"
        ):
            AccuWeather(VALID_API_KEY, session, latitude=55.55, longitude="78.00")


@pytest.mark.asyncio
async def test_invalid_coordinates_2():
    """Test with invalid coordinates."""
    async with ClientSession() as session:
        with pytest.raises(
            InvalidCoordinatesError, match="Your coordinates are invalid"
        ):
            AccuWeather(VALID_API_KEY, session, latitude=199.99, longitude=90.0)


@pytest.mark.asyncio
async def test_api_error():
    """Test with API error."""
    payload = {
        "Code": "ServiceError",
        "Message": "API error.",
    }

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(
            "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=32-character-string-1234567890qw&q=52.0677904%252C19.4795644",
            payload=payload,
            status=404,
        )
        accuweather = AccuWeather(
            VALID_API_KEY, session, latitude=LATITUDE, longitude=LONGITUDE
        )
        with pytest.raises(
            ApiError, match="Invalid response from AccuWeather API: 404"
        ):
            await accuweather.async_get_location()

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
        session_mock.get(
            "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=32-character-string-1234567890qw&q=52.0677904%252C19.4795644",
            payload=payload,
            status=503,
        )
        accuweather = AccuWeather(
            VALID_API_KEY, session, latitude=LATITUDE, longitude=LONGITUDE
        )
        with pytest.raises(
            RequestsExceededError,
            match="The allowed number of requests has been exceeded",
        ):
            await accuweather.async_get_location()

    await session.close()
