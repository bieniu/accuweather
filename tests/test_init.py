"""Tests for accuweather package."""
from http import HTTPStatus

import aiohttp
import orjson
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


@pytest.fixture()
def location_data():
    """Location data fixture."""
    with open("tests/fixtures/location_data.json", encoding="utf-8") as file:
        return orjson.loads(file.read())


@pytest.fixture()
def current_condition_data():
    """Weather current condition data fixture."""
    with open("tests/fixtures/current_condition_data.json", encoding="utf-8") as file:
        return orjson.loads(file.read())


@pytest.fixture()
def daily_forecast_data():
    """Daily forecast data fixture."""
    with open("tests/fixtures/daily_forecast_data.json", encoding="utf-8") as file:
        return orjson.loads(file.read())


@pytest.fixture()
def hourly_forecast_data():
    """Hourly forecast data fixture."""
    with open("tests/fixtures/hourly_forecast_data.json", encoding="utf-8") as file:
        return orjson.loads(file.read())


@pytest.mark.asyncio
async def test_get_location(location_data):
    """Test with valid location data."""
    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(
            "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=32-character-string-1234567890qw&q=52.0677904%252C19.4795644&language=en-us",
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
async def test_get_current_conditions(location_data, current_condition_data):
    """Test with valid current condition data."""
    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(
            "https://dataservice.accuweather.com/currentconditions/v1/268068?apikey=32-character-string-1234567890qw&details=true&language=en-us",
            payload=current_condition_data,
            headers=HEADERS,
        )
        session_mock.get(
            "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=32-character-string-1234567890qw&q=52.0677904%252C19.4795644&language=en-us",
            payload=location_data,
            headers=HEADERS,
        )
        accuweather = AccuWeather(
            VALID_API_KEY, session, latitude=LATITUDE, longitude=LONGITUDE
        )
        current_conditions = await accuweather.async_get_current_conditions()

    await session.close()

    assert current_conditions["WeatherIcon"] == 7
    assert current_conditions["WeatherText"] == "Cloudy"
    assert current_conditions["HasPrecipitation"] is False
    assert current_conditions["PrecipitationType"] is None
    assert current_conditions["Temperature"]["Metric"]["Value"] == 13.4
    assert current_conditions["Temperature"]["Metric"]["Unit"] == "C"
    assert current_conditions["Temperature"]["Imperial"]["Value"] == 56
    assert current_conditions["Temperature"]["Imperial"]["Unit"] == "F"
    assert current_conditions["UVIndex"] == 2
    assert current_conditions["UVIndexText"] == "low"
    assert current_conditions["PressureTendency"]["LocalizedText"] == "steady"

    assert accuweather.requests_remaining == 23


@pytest.mark.asyncio
async def test_get_daily_forecast(location_data, daily_forecast_data):
    """Test with valid daily forecast data."""
    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(
            "https://dataservice.accuweather.com/forecasts/v1/daily/5day/268068?apikey=32-character-string-1234567890qw&details=true&metric=true&language=en-us",
            payload=daily_forecast_data,
            headers=HEADERS,
        )
        session_mock.get(
            "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=32-character-string-1234567890qw&q=52.0677904%252C19.4795644&language=en-us",
            payload=location_data,
            headers=HEADERS,
        )

        accuweather = AccuWeather(
            VALID_API_KEY, session, latitude=LATITUDE, longitude=LONGITUDE
        )
        forecast = await accuweather.async_get_daily_forecast()

    await session.close()

    assert forecast[0]["IconDay"] == 18
    assert forecast[0]["IconPhraseDay"] == "rain"
    assert forecast[0]["PrecipitationProbabilityDay"] == 91
    assert forecast[0]["WindDay"]["Speed"]["Value"] == 16.7
    assert forecast[0]["TemperatureMax"]["Value"] == 16.2
    assert forecast[0]["TemperatureMax"]["Unit"] == "C"
    assert forecast[0]["UVIndex"]["Category"] == "low"
    assert forecast[0]["PrecipitationTypeDay"] == "rain"
    assert forecast[0]["PrecipitationIntensityDay"] == "light"
    assert forecast[0]["ShortPhraseDay"] == "Cooler with periods of rain"
    assert forecast[0]["LongPhraseDay"] == "Cooler with periods of rain"
    assert forecast[0]["AirQuality"]["Category"] == "unhealthy"
    assert accuweather.requests_remaining == 23


@pytest.mark.asyncio
async def test_get_hourly_forecast(location_data, hourly_forecast_data):
    """Test with valid hourly forecast data."""
    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(
            "https://dataservice.accuweather.com/forecasts/v1/hourly/12hour/268068?apikey=32-character-string-1234567890qw&details=true&metric=true&language=en-us",
            payload=hourly_forecast_data,
            headers=HEADERS,
        )
        session_mock.get(
            "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=32-character-string-1234567890qw&q=52.0677904%252C19.4795644&language=en-us",
            payload=location_data,
            headers=HEADERS,
        )

        accuweather = AccuWeather(
            VALID_API_KEY, session, latitude=LATITUDE, longitude=LONGITUDE
        )
        forecast = await accuweather.async_get_hourly_forecast()

    await session.close()

    assert forecast[0]["WeatherIcon"] == 18
    assert forecast[0]["IconPhrase"] == "rain"
    assert forecast[0]["HasPrecipitation"] is True
    assert forecast[0]["UVIndex"] == 2
    assert forecast[0]["UVIndexText"] == "low"
    assert forecast[0]["PrecipitationType"] == "rain"
    assert forecast[0]["PrecipitationIntensity"] == "light"
    assert forecast[0]["Temperature"]["Value"] == 14.7
    assert forecast[0]["Temperature"]["Unit"] == "C"
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
            "https://dataservice.accuweather.com/currentconditions/v1/268068?apikey=32-character-string-1234567890qw&details=true&language=en-us",
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
            "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=32-character-string-1234567890qw&q=52.0677904%252C19.4795644&language=en-us",
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
            "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=32-character-string-1234567890qw&q=52.0677904%252C19.4795644&language=en-us",
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
