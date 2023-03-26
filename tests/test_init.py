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

    assert current_conditions.apparent_temperature.value == 0.6
    assert current_conditions.apparent_temperature.unit == "°C"
    assert current_conditions.ceiling.value == 305.0
    assert current_conditions.ceiling.unit == "m"
    assert current_conditions.cloud_cover.value == 90
    assert current_conditions.cloud_cover.unit == "%"
    assert current_conditions.date_time_epoch == 1678383120
    assert str(current_conditions.date_time) == "2023-03-09 18:32:00+01:00"
    assert current_conditions.dew_point.value == -1.7
    assert current_conditions.dew_point.unit == "°C"
    assert current_conditions.has_precipitation is False
    assert current_conditions.indoor_relative_humidity.value == 38
    assert current_conditions.indoor_relative_humidity.unit == "%"
    assert current_conditions.is_day_time is False
    assert current_conditions.precipitation_past_12_hours.value == 7.2
    assert current_conditions.precipitation_past_12_hours.unit == "mm"
    assert current_conditions.precipitation_past_18_hours.value == 10.6
    assert current_conditions.precipitation_past_18_hours.unit == "mm"
    assert current_conditions.precipitation_past_24_hours.value == 13.9
    assert current_conditions.precipitation_past_24_hours.unit == "mm"
    assert current_conditions.precipitation_past_3_hours.value == 0.0
    assert current_conditions.precipitation_past_3_hours.unit == "mm"
    assert current_conditions.precipitation_past_6_hours.value == 3.3
    assert current_conditions.precipitation_past_6_hours.unit == "mm"
    assert current_conditions.precipitation_past_9_hours.value == 7.2
    assert current_conditions.precipitation_past_9_hours.unit == "mm"
    assert current_conditions.precipitation_past_hour.value == 0.0
    assert current_conditions.precipitation_past_hour.unit == "mm"
    assert current_conditions.precipitation_type is None
    assert current_conditions.pressure.value == 1001.0
    assert current_conditions.pressure.unit == "mbar"
    assert current_conditions.pressure.text == "rising"
    assert current_conditions.real_feel_temperature_shade.value == -2.1
    assert current_conditions.real_feel_temperature_shade.unit == "°C"
    assert current_conditions.real_feel_temperature_shade.text == "cold"
    assert current_conditions.real_feel_temperature.value == -2.1
    assert current_conditions.real_feel_temperature.unit == "°C"
    assert current_conditions.real_feel_temperature.text == "cold"
    assert current_conditions.relative_humidity.value == 85
    assert current_conditions.relative_humidity.unit == "%"
    assert current_conditions.temperature.value == 0.5
    assert current_conditions.temperature.unit == "°C"
    assert current_conditions.uv_index.value == 0
    assert current_conditions.uv_index.unit is None
    assert current_conditions.uv_index.text == "low"
    assert current_conditions.visibility.value == 16.1
    assert current_conditions.visibility.unit == "km"
    assert current_conditions.weather_icon == 38
    assert current_conditions.weather_text == "mostly cloudy"
    assert current_conditions.wet_bulb_temperature.value == -0.3
    assert current_conditions.wet_bulb_temperature.unit == "°C"
    assert current_conditions.wind_chill_temperature.value == -2.8
    assert current_conditions.wind_chill_temperature.unit == "°C"
    assert current_conditions.wind_direction.value == 90
    assert current_conditions.wind_direction.unit == "°"
    assert current_conditions.wind_direction.text == "e"
    assert current_conditions.wind_gust.value == 18.6
    assert current_conditions.wind_gust.unit == "km/h"
    assert current_conditions.wind_speed.value == 10.7
    assert current_conditions.wind_speed.unit == "km/h"
    assert accuweather.requests_remaining == 23


@pytest.mark.asyncio
async def test_get_current_conditions_imperial():
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
            VALID_API_KEY, session, latitude=LATITUDE, longitude=LONGITUDE, metric=False
        )
        current_conditions = await accuweather.async_get_current_conditions()

    await session.close()

    assert current_conditions.apparent_temperature.value == 33.0
    assert current_conditions.apparent_temperature.unit == "°F"
    assert current_conditions.ceiling.value == 1000.0
    assert current_conditions.ceiling.unit == "ft"
    assert current_conditions.cloud_cover.value == 90
    assert current_conditions.cloud_cover.unit == "%"
    assert current_conditions.date_time_epoch == 1678383120
    assert str(current_conditions.date_time) == "2023-03-09 18:32:00+01:00"
    assert current_conditions.dew_point.value == 29.0
    assert current_conditions.dew_point.unit == "°F"
    assert current_conditions.has_precipitation is False
    assert current_conditions.indoor_relative_humidity.value == 38
    assert current_conditions.indoor_relative_humidity.unit == "%"
    assert current_conditions.is_day_time is False
    assert current_conditions.precipitation_past_12_hours.value == 0.28
    assert current_conditions.precipitation_past_12_hours.unit == "in"
    assert current_conditions.precipitation_past_18_hours.value == 0.42
    assert current_conditions.precipitation_past_18_hours.unit == "in"
    assert current_conditions.precipitation_past_24_hours.value == 0.55
    assert current_conditions.precipitation_past_24_hours.unit == "in"
    assert current_conditions.precipitation_past_3_hours.value == 0.0
    assert current_conditions.precipitation_past_3_hours.unit == "in"
    assert current_conditions.precipitation_past_6_hours.value == 0.13
    assert current_conditions.precipitation_past_6_hours.unit == "in"
    assert current_conditions.precipitation_past_9_hours.value == 0.28
    assert current_conditions.precipitation_past_9_hours.unit == "in"
    assert current_conditions.precipitation_past_hour.value == 0.0
    assert current_conditions.precipitation_past_hour.unit == "in"
    assert current_conditions.precipitation_type is None
    assert current_conditions.pressure.value == 29.56
    assert current_conditions.pressure.unit == "inHg"
    assert current_conditions.pressure.text == "rising"
    assert current_conditions.real_feel_temperature_shade.value == 28.0
    assert current_conditions.real_feel_temperature_shade.unit == "°F"
    assert current_conditions.real_feel_temperature_shade.text == "cold"
    assert current_conditions.real_feel_temperature.value == 28.0
    assert current_conditions.real_feel_temperature.unit == "°F"
    assert current_conditions.real_feel_temperature.text == "cold"
    assert current_conditions.relative_humidity.value == 85
    assert current_conditions.relative_humidity.unit == "%"
    assert current_conditions.temperature.value == 33.0
    assert current_conditions.temperature.unit == "°F"
    assert current_conditions.uv_index.value == 0
    assert current_conditions.uv_index.unit is None
    assert current_conditions.uv_index.text == "low"
    assert current_conditions.visibility.value == 10.0
    assert current_conditions.visibility.unit == "mi"
    assert current_conditions.weather_icon == 38
    assert current_conditions.weather_text == "mostly cloudy"
    assert current_conditions.wet_bulb_temperature.value == 32.0
    assert current_conditions.wet_bulb_temperature.unit == "°F"
    assert current_conditions.wind_chill_temperature.value == 27.0
    assert current_conditions.wind_chill_temperature.unit == "°F"
    assert current_conditions.wind_direction.value == 90
    assert current_conditions.wind_direction.unit == "°"
    assert current_conditions.wind_direction.text == "e"
    assert current_conditions.wind_gust.value == 11.5
    assert current_conditions.wind_gust.unit == "mi/h"
    assert current_conditions.wind_speed.value == 6.6
    assert current_conditions.wind_speed.unit == "mi/h"
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
