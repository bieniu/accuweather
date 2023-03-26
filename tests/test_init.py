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
    with open("tests/fixtures/location.json", encoding="utf-8") as file:
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
async def test_get_current_conditions_metric():
    """Test with valid current condition data."""
    with open("tests/fixtures/current_conditions.json", encoding="utf-8") as file:
        current_condition_data = json.load(file)
    with open("tests/fixtures/location.json", encoding="utf-8") as file:
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
    with open("tests/fixtures/current_conditions.json", encoding="utf-8") as file:
        current_condition_data = json.load(file)
    with open("tests/fixtures/location.json", encoding="utf-8") as file:
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
async def test_get_daily_forecast_metric():
    """Test with valid forecast data."""
    with open("tests/fixtures/daily_forecast_metric.json", encoding="utf-8") as file:
        daily_forecast_data = json.load(file)
    with open("tests/fixtures/location.json", encoding="utf-8") as file:
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

    assert len(forecast) == 5
    assert forecast[0].air_quality.value == 0
    assert forecast[0].air_quality.unit is None
    assert forecast[0].air_quality.text == "good"
    assert forecast[0].cloud_cover_day.value == 91
    assert forecast[0].cloud_cover_day.unit == "%"
    assert forecast[0].cloud_cover_night.value == 85
    assert forecast[0].cloud_cover_night.unit == "%"
    assert forecast[0].date_time_epoch == 1679551200
    assert str(forecast[0].date_time) == "2023-03-23 07:00:00+01:00"
    assert forecast[0].grass_pollen.value == 0
    assert forecast[0].grass_pollen.unit == "p/m³"
    assert forecast[0].grass_pollen.text == "low"
    assert forecast[0].hours_of_ice_day.value == 0.0
    assert forecast[0].hours_of_ice_day.unit == "h"
    assert forecast[0].hours_of_ice_night.value == 0.0
    assert forecast[0].hours_of_ice_night.unit == "h"
    assert forecast[0].hours_of_precipitation_day.value == 0.0
    assert forecast[0].hours_of_precipitation_day.unit == "h"
    assert forecast[0].hours_of_precipitation_night.value == 0.0
    assert forecast[0].hours_of_precipitation_night.unit == "h"
    assert forecast[0].hours_of_rain_day.value == 0.0
    assert forecast[0].hours_of_rain_day.unit == "h"
    assert forecast[0].hours_of_rain_night.value == 0.0
    assert forecast[0].hours_of_rain_night.unit == "h"
    assert forecast[0].hours_of_snow_day.value == 0.0
    assert forecast[0].hours_of_snow_day.unit == "h"
    assert forecast[0].hours_of_snow_night.value == 0.0
    assert forecast[0].hours_of_snow_night.unit == "h"
    assert forecast[0].hours_of_sun.value == 1.4
    assert forecast[0].hours_of_sun.unit == "h"
    assert forecast[0].ice_probability_day.value == 0
    assert forecast[0].ice_probability_day.unit == "%"
    assert forecast[0].ice_probability_night.value == 0
    assert forecast[0].ice_probability_night.unit == "%"
    assert forecast[0].mold.value == 300
    assert forecast[0].mold.unit == "p/m³"
    assert forecast[0].mold.text == "low"
    assert forecast[0].precipitation_ice_day.value == 0.0
    assert forecast[0].precipitation_ice_day.unit == "mm"
    assert forecast[0].precipitation_ice_night.value == 0.0
    assert forecast[0].precipitation_ice_night.unit == "mm"
    assert forecast[0].precipitation_liquid_day.value == 0.0
    assert forecast[0].precipitation_liquid_day.unit == "mm"
    assert forecast[0].precipitation_liquid_night.value == 0.0
    assert forecast[0].precipitation_liquid_night.unit == "mm"
    assert forecast[0].precipitation_probability_day.value == 25
    assert forecast[0].precipitation_probability_day.unit == "%"
    assert forecast[0].precipitation_probability_night.value == 25
    assert forecast[0].precipitation_probability_night.unit == "%"
    assert forecast[0].precipitation_rain_day.value == 0.0
    assert forecast[0].precipitation_rain_day.unit == "mm"
    assert forecast[0].precipitation_rain_night.value == 0.0
    assert forecast[0].precipitation_rain_night.unit == "mm"
    assert forecast[0].precipitation_snow_day.value == 0.0
    assert forecast[0].precipitation_snow_day.unit == "cm"
    assert forecast[0].precipitation_snow_night.value == 0.0
    assert forecast[0].precipitation_snow_night.unit == "cm"
    assert forecast[0].ragweed_pollen.value == 0
    assert forecast[0].ragweed_pollen.unit == "p/m³"
    assert forecast[0].ragweed_pollen.text == "low"
    assert forecast[0].rain_probability_day.value == 25
    assert forecast[0].rain_probability_day.unit == "%"
    assert forecast[0].rain_probability_night.value == 25
    assert forecast[0].rain_probability_night.unit == "%"
    assert forecast[0].real_feel_temperature_max.value == 13.4
    assert forecast[0].real_feel_temperature_max.unit == "°C"
    assert forecast[0].real_feel_temperature_min.value == 5.9
    assert forecast[0].real_feel_temperature_min.unit == "°C"
    assert forecast[0].real_feel_temperature_shade_max.value == 12.9
    assert forecast[0].real_feel_temperature_shade_max.unit == "°C"
    assert forecast[0].real_feel_temperature_shade_min.value == 5.9
    assert forecast[0].real_feel_temperature_shade_min.unit == "°C"
    assert forecast[0].snow_probability_day.value == 0
    assert forecast[0].snow_probability_day.unit == "%"
    assert forecast[0].snow_probability_night.value == 0
    assert forecast[0].snow_probability_night.unit == "%"
    assert forecast[0].solar_irradiance_day.value == 2396.9
    assert forecast[0].solar_irradiance_day.unit == "W/m²"
    assert forecast[0].solar_irradiance_night.value == 8.6
    assert forecast[0].solar_irradiance_night.unit == "W/m²"
    assert forecast[0].temperature_max.value == 16.1
    assert forecast[0].temperature_max.unit == "°C"
    assert forecast[0].thunderstorm_probability_day.value == 0
    assert forecast[0].thunderstorm_probability_day.unit == "%"
    assert forecast[0].thunderstorm_probability_night.value == 0
    assert forecast[0].thunderstorm_probability_night.unit == "%"
    assert forecast[0].tree_pollen.value == 2
    assert forecast[0].tree_pollen.unit == "p/m³"
    assert forecast[0].tree_pollen.text == "low"
    assert forecast[0].uv_index.value == 2
    assert forecast[0].uv_index.unit is None
    assert forecast[0].uv_index.text == "low"
    assert forecast[0].weather_icon_day == 7
    assert forecast[0].weather_icon_night == 38
    assert forecast[0].weather_long_text_day == "cloudy and warm"
    assert forecast[0].weather_long_text_night == "mostly cloudy and mild"
    assert forecast[0].weather_text_day == "cloudy"
    assert forecast[0].weather_text_night == "mostly cloudy"
    assert forecast[0].wind_direction_day.value == 229
    assert forecast[0].wind_direction_day.unit == "°"
    assert forecast[0].wind_direction_day.text == "sw"
    assert forecast[0].wind_direction_night.value == 225
    assert forecast[0].wind_direction_night.unit == "°"
    assert forecast[0].wind_direction_night.text == "sw"
    assert forecast[0].wind_gust_day.value == 48.2
    assert forecast[0].wind_gust_day.unit == "km/h"
    assert forecast[0].wind_gust_night.value == 31.5
    assert forecast[0].wind_gust_night.unit == "km/h"
    assert forecast[0].wind_speed_day.value == 22.2
    assert forecast[0].wind_speed_day.unit == "km/h"
    assert forecast[0].wind_speed_night.value == 14.8
    assert forecast[0].wind_speed_night.unit == "km/h"
    assert accuweather.requests_remaining == 23


@pytest.mark.asyncio
async def test_get_daily_forecast_imperial():
    """Test with valid forecast data."""
    with open("tests/fixtures/daily_forecast_imperial.json", encoding="utf-8") as file:
        daily_forecast_data = json.load(file)
    with open("tests/fixtures/location.json", encoding="utf-8") as file:
        location_data = json.load(file)

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(
            "https://dataservice.accuweather.com/forecasts/v1/daily/5day/268068?apikey=32-character-string-1234567890qw&details=true&metric=false",
            payload=daily_forecast_data,
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
        forecast = await accuweather.async_get_daily_forecast()

    await session.close()

    assert len(forecast) == 5
    assert forecast[0].air_quality.value == 0
    assert forecast[0].air_quality.unit is None
    assert forecast[0].air_quality.text == "good"
    assert forecast[0].cloud_cover_day.value == 80
    assert forecast[0].cloud_cover_day.unit == "%"
    assert forecast[0].cloud_cover_night.value == 94
    assert forecast[0].cloud_cover_night.unit == "%"
    assert forecast[0].date_time_epoch == 1679806800
    assert str(forecast[0].date_time) == "2023-03-26 07:00:00+02:00"
    assert forecast[0].grass_pollen.value == 0
    assert forecast[0].grass_pollen.unit == "p/m³"
    assert forecast[0].grass_pollen.text == "low"
    assert forecast[0].has_precipitation_day is True
    assert forecast[0].has_precipitation_night is True
    assert forecast[0].hours_of_ice_day.value == 0.0
    assert forecast[0].hours_of_ice_day.unit == "h"
    assert forecast[0].hours_of_ice_night.value == 0.0
    assert forecast[0].hours_of_ice_night.unit == "h"
    assert forecast[0].hours_of_precipitation_day.value == 1.0
    assert forecast[0].hours_of_precipitation_day.unit == "h"
    assert forecast[0].hours_of_precipitation_night.value == 1.0
    assert forecast[0].hours_of_precipitation_night.unit == "h"
    assert forecast[0].hours_of_rain_day.value == 1.0
    assert forecast[0].hours_of_rain_day.unit == "h"
    assert forecast[0].hours_of_rain_night.value == 1.0
    assert forecast[0].hours_of_rain_night.unit == "h"
    assert forecast[0].hours_of_snow_day.value == 0.0
    assert forecast[0].hours_of_snow_day.unit == "h"
    assert forecast[0].hours_of_snow_night.value == 0.0
    assert forecast[0].hours_of_snow_night.unit == "h"
    assert forecast[0].hours_of_sun.value == 2.6
    assert forecast[0].hours_of_sun.unit == "h"
    assert forecast[0].ice_probability_day.value == 0
    assert forecast[0].ice_probability_day.unit == "%"
    assert forecast[0].ice_probability_night.value == 0
    assert forecast[0].ice_probability_night.unit == "%"
    assert forecast[0].mold.value == 0
    assert forecast[0].mold.unit == "p/m³"
    assert forecast[0].mold.text == "low"
    assert forecast[0].precipitation_ice_day.value == 0.0
    assert forecast[0].precipitation_ice_day.unit == "in"
    assert forecast[0].precipitation_ice_night.value == 0.0
    assert forecast[0].precipitation_ice_night.unit == "in"
    assert forecast[0].precipitation_liquid_day.value == 0.03
    assert forecast[0].precipitation_liquid_day.unit == "in"
    assert forecast[0].precipitation_liquid_night.value == 0.04
    assert forecast[0].precipitation_liquid_night.unit == "in"
    assert forecast[0].precipitation_probability_day.value == 43
    assert forecast[0].precipitation_probability_day.unit == "%"
    assert forecast[0].precipitation_probability_night.value == 60
    assert forecast[0].precipitation_probability_night.unit == "%"
    assert forecast[0].precipitation_rain_day.value == 0.03
    assert forecast[0].precipitation_rain_day.unit == "in"
    assert forecast[0].precipitation_rain_night.value == 0.04
    assert forecast[0].precipitation_rain_night.unit == "in"
    assert forecast[0].precipitation_snow_day.value == 0.0
    assert forecast[0].precipitation_snow_day.unit == "in"
    assert forecast[0].precipitation_snow_night.value == 0.0
    assert forecast[0].precipitation_snow_night.unit == "in"
    assert forecast[0].precipitation_type_day == "rain"
    assert forecast[0].precipitation_type_night == "rain"
    assert forecast[0].ragweed_pollen.value == 0
    assert forecast[0].ragweed_pollen.unit == "p/m³"
    assert forecast[0].ragweed_pollen.text == "low"
    assert forecast[0].rain_probability_day.value == 43
    assert forecast[0].rain_probability_day.unit == "%"
    assert forecast[0].rain_probability_night.value == 60
    assert forecast[0].rain_probability_night.unit == "%"
    assert forecast[0].real_feel_temperature_max.value == 45.0
    assert forecast[0].real_feel_temperature_max.unit == "°F"
    assert forecast[0].real_feel_temperature_min.value == 28.0
    assert forecast[0].real_feel_temperature_min.unit == "°F"
    assert forecast[0].real_feel_temperature_shade_max.value == 44.0
    assert forecast[0].real_feel_temperature_shade_max.unit == "°F"
    assert forecast[0].real_feel_temperature_shade_min.value == 28.0
    assert forecast[0].real_feel_temperature_shade_min.unit == "°F"
    assert forecast[0].snow_probability_day.value == 0
    assert forecast[0].snow_probability_day.unit == "%"
    assert forecast[0].snow_probability_night.value == 0
    assert forecast[0].snow_probability_night.unit == "%"
    assert forecast[0].solar_irradiance_day.value == 2872.9
    assert forecast[0].solar_irradiance_day.unit == "W/m²"
    assert forecast[0].solar_irradiance_night.value == 16.4
    assert forecast[0].solar_irradiance_night.unit == "W/m²"
    assert forecast[0].temperature_max.value == 51.0
    assert forecast[0].temperature_max.unit == "°F"
    assert forecast[0].thunderstorm_probability_day.value == 9
    assert forecast[0].thunderstorm_probability_day.unit == "%"
    assert forecast[0].thunderstorm_probability_night.value == 12
    assert forecast[0].thunderstorm_probability_night.unit == "%"
    assert forecast[0].tree_pollen.value == 2
    assert forecast[0].tree_pollen.unit == "p/m³"
    assert forecast[0].tree_pollen.text == "low"
    assert forecast[0].uv_index.value == 1
    assert forecast[0].uv_index.unit is None
    assert forecast[0].uv_index.text == "low"
    assert forecast[0].weather_icon_day == 13
    assert forecast[0].weather_icon_night == 12
    assert (
        forecast[0].weather_long_text_day
        == "variable cloudiness with a shower in places; breezy this morning"
    )
    assert forecast[0].weather_long_text_night == "cloudy with a couple of showers late"
    assert forecast[0].weather_text_day == "mostly cloudy w/ showers"
    assert forecast[0].weather_text_night == "showers"
    assert forecast[0].wind_direction_day.value == 255
    assert forecast[0].wind_direction_day.unit == "°"
    assert forecast[0].wind_direction_day.text == "wsw"
    assert forecast[0].wind_direction_night.value == 320
    assert forecast[0].wind_direction_night.unit == "°"
    assert forecast[0].wind_direction_night.text == "nw"
    assert forecast[0].wind_gust_day.value == 27.6
    assert forecast[0].wind_gust_day.unit == "mi/h"
    assert forecast[0].wind_gust_night.value == 16.1
    assert forecast[0].wind_gust_night.unit == "mi/h"
    assert forecast[0].wind_speed_day.value == 15.0
    assert forecast[0].wind_speed_day.unit == "mi/h"
    assert forecast[0].wind_speed_night.value == 4.6
    assert forecast[0].wind_speed_night.unit == "mi/h"
    assert accuweather.requests_remaining == 23


@pytest.mark.asyncio
async def test_get_hourly_forecast_metric():
    """Test with valid hourly_forecast data."""
    with open("tests/fixtures/hourly_forecast_metric.json", encoding="utf-8") as file:
        hourly_forecast_data = json.load(file)
    with open("tests/fixtures/location.json", encoding="utf-8") as file:
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

    assert len(forecast) == 12
    assert forecast[0].ceiling.value == 884.0
    assert forecast[0].ceiling.unit == "m"
    assert forecast[0].cloud_cover.value == 76
    assert forecast[0].cloud_cover.unit == "%"
    assert str(forecast[0].date_time) == "2023-03-25 15:00:00+01:00"
    assert forecast[0].date_time_epoch == 1679752800
    assert forecast[0].dew_point.value == 5.6
    assert forecast[0].dew_point.unit == "°C"
    assert forecast[0].has_precipitation is True
    assert forecast[0].ice_probability.value == 0
    assert forecast[0].ice_probability.unit == "%"
    assert forecast[0].indoor_relative_humidity.value == 66
    assert forecast[0].indoor_relative_humidity.unit == "%"
    assert forecast[0].is_daylight is True
    assert forecast[0].precipitation_ice.value == 0.0
    assert forecast[0].precipitation_ice.unit == "mm"
    assert forecast[0].precipitation_liquid.value == 0.3
    assert forecast[0].precipitation_liquid.unit == "mm"
    assert forecast[0].precipitation_probability.value == 60
    assert forecast[0].precipitation_probability.unit == "%"
    assert forecast[0].precipitation_rain.value == 0.3
    assert forecast[0].precipitation_rain.unit == "mm"
    assert forecast[0].precipitation_snow.value == 0.0
    assert forecast[0].precipitation_snow.unit == "cm"
    assert forecast[0].precipitation_type == "rain"
    assert forecast[0].rain_probability.value == 60
    assert forecast[0].rain_probability.unit == "%"
    assert forecast[0].real_feel_temperature_shade.value == 6.7
    assert forecast[0].real_feel_temperature_shade.unit == "°C"
    assert forecast[0].real_feel_temperature.value == 7.3
    assert forecast[0].real_feel_temperature.unit == "°C"
    assert forecast[0].relative_humidity.value == 66
    assert forecast[0].relative_humidity.unit == "%"
    assert forecast[0].snow_probability.value == 0
    assert forecast[0].snow_probability.unit == "%"
    assert forecast[0].solar_irradiance.value == 293.5
    assert forecast[0].solar_irradiance.unit == "W/m²"
    assert forecast[0].temperature.value == 11.7
    assert forecast[0].temperature.unit == "°C"
    assert forecast[0].thunderstorm_probability.value == 6
    assert forecast[0].thunderstorm_probability.unit == "%"
    assert forecast[0].uv_index.value == 1
    assert forecast[0].uv_index.unit is None
    assert forecast[0].uv_index.text == "low"
    assert forecast[0].visibility.value == 9.7
    assert forecast[0].visibility.unit == "km"
    assert forecast[0].weather_icon == 18
    assert forecast[0].weather_text == "rain"
    assert forecast[0].wet_bulb_temperature.value == 8.9
    assert forecast[0].wet_bulb_temperature.unit == "°C"
    assert forecast[0].wind_direction.value == 235
    assert forecast[0].wind_direction.unit == "°"
    assert forecast[0].wind_direction.text == "sw"
    assert forecast[0].wind_gust.value == 35.2
    assert forecast[0].wind_gust.unit == "km/h"
    assert forecast[0].wind_speed.value == 22.2
    assert forecast[0].wind_speed.unit == "km/h"
    assert accuweather.requests_remaining == 23


@pytest.mark.asyncio
async def test_get_hourly_forecast_imperial():
    """Test with valid hourly_forecast data."""
    with open("tests/fixtures/hourly_forecast_imperial.json", encoding="utf-8") as file:
        hourly_forecast_data = json.load(file)
    with open("tests/fixtures/location.json", encoding="utf-8") as file:
        location_data = json.load(file)

    session = aiohttp.ClientSession()

    with aioresponses() as session_mock:
        session_mock.get(
            "https://dataservice.accuweather.com/forecasts/v1/hourly/12hour/268068?apikey=32-character-string-1234567890qw&details=true&metric=false",
            payload=hourly_forecast_data,
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
        forecast = await accuweather.async_get_hourly_forecast()

    await session.close()

    assert len(forecast) == 12
    assert forecast[0].ceiling.value == 22700.0
    assert forecast[0].ceiling.unit == "ft"
    assert forecast[0].cloud_cover.value == 93
    assert forecast[0].cloud_cover.unit == "%"
    assert str(forecast[0].date_time) == "2023-03-26 22:00:00+02:00"
    assert forecast[0].date_time_epoch == 1679860800
    assert forecast[0].dew_point.value == 37.0
    assert forecast[0].dew_point.unit == "°F"
    assert forecast[0].has_precipitation is False
    assert forecast[0].ice_probability.value == 0
    assert forecast[0].ice_probability.unit == "%"
    assert forecast[0].indoor_relative_humidity.value == 84
    assert forecast[0].indoor_relative_humidity.unit == "%"
    assert forecast[0].is_daylight is False
    assert forecast[0].precipitation_ice.value == 0.0
    assert forecast[0].precipitation_ice.unit == "in"
    assert forecast[0].precipitation_liquid.value == 0.0
    assert forecast[0].precipitation_liquid.unit == "in"
    assert forecast[0].precipitation_probability.value == 20
    assert forecast[0].precipitation_probability.unit == "%"
    assert forecast[0].precipitation_rain.value == 0.0
    assert forecast[0].precipitation_rain.unit == "in"
    assert forecast[0].precipitation_snow.value == 0.0
    assert forecast[0].precipitation_snow.unit == "in"
    assert forecast[0].precipitation_type is None
    assert forecast[0].rain_probability.value == 20
    assert forecast[0].rain_probability.unit == "%"
    assert forecast[0].real_feel_temperature_shade.value == 44.0
    assert forecast[0].real_feel_temperature_shade.unit == "°F"
    assert forecast[0].real_feel_temperature.value == 44.0
    assert forecast[0].real_feel_temperature.unit == "°F"
    assert forecast[0].relative_humidity.value == 84
    assert forecast[0].relative_humidity.unit == "%"
    assert forecast[0].snow_probability.value == 0
    assert forecast[0].snow_probability.unit == "%"
    assert forecast[0].solar_irradiance.value == 0.0
    assert forecast[0].solar_irradiance.unit == "W/m²"
    assert forecast[0].temperature.value == 42.0
    assert forecast[0].temperature.unit == "°F"
    assert forecast[0].thunderstorm_probability.value == 0
    assert forecast[0].thunderstorm_probability.unit == "%"
    assert forecast[0].uv_index.value == 0
    assert forecast[0].uv_index.unit is None
    assert forecast[0].uv_index.text == "low"
    assert forecast[0].visibility.value == 10.0
    assert forecast[0].visibility.unit == "mi"
    assert forecast[0].weather_icon == 7
    assert forecast[0].weather_text == "cloudy"
    assert forecast[0].wet_bulb_temperature.value == 40.0
    assert forecast[0].wet_bulb_temperature.unit == "°F"
    assert forecast[0].wind_direction.value == 231
    assert forecast[0].wind_direction.unit == "°"
    assert forecast[0].wind_direction.text == "sw"
    assert forecast[0].wind_gust.value == 6.9
    assert forecast[0].wind_gust.unit == "mi/h"
    assert forecast[0].wind_speed.value == 2.3
    assert forecast[0].wind_speed.unit == "mi/h"
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
