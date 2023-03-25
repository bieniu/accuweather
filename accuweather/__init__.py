"""Python wrapper for getting weather data from AccueWeather for Limited Trial."""

from __future__ import annotations

import logging
from datetime import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

import orjson
from aiohttp import ClientSession

from .const import (
    ATTR_CURRENT_CONDITIONS,
    ATTR_FORECAST_DAILY_5,
    ATTR_FORECAST_HOURLY_12,
    ATTR_GEOPOSITION,
    ENDPOINT,
    HTTP_HEADERS,
    MAX_API_KEY_LENGTH,
    MAX_LATITUDE,
    MAX_LONGITUDE,
    REMOVE_FROM_FORECAST,
    REQUESTS_EXCEEDED,
    UNIT_DEGREES,
    UNIT_PERCENTAGE,
    URLS,
)
from .exceptions import (
    ApiError,
    InvalidApiKeyError,
    InvalidCoordinatesError,
    RequestsExceededError,
)
from .model import CurrentCondition, ForecastDay, Value

_LOGGER = logging.getLogger(__name__)


class AccuWeather:
    """Main class to perform AccuWeather API requests."""

    def __init__(  # noqa: PLR0913
        self,
        api_key: str,
        session: ClientSession,
        latitude: float | None = None,
        longitude: float | None = None,
        location_key: str | None = None,
        metric: bool = True,
    ) -> None:
        """Initialize."""
        if not self._valid_api_key(api_key):
            raise InvalidApiKeyError(
                "Your API Key must be a 32-character hexadecimal string"
            )
        if not location_key and not self._valid_coordinates(latitude, longitude):
            raise InvalidCoordinatesError("Your coordinates are invalid")

        self.latitude = latitude
        self.longitude = longitude
        self._api_key = api_key
        self._session = session
        self._location_key = location_key
        self._location_name: str | None = None
        self._requests_remaining: int | None = None
        self.unit_system: str = "Metric" if metric else "Imperial"

    @staticmethod
    def _valid_coordinates(
        latitude: float | int | None, longitude: float | int | None
    ) -> bool:
        """Return True if coordinates are valid."""
        if (
            isinstance(latitude, (int, float))
            and isinstance(longitude, (int, float))
            and abs(latitude) <= MAX_LATITUDE
            and abs(longitude) <= MAX_LONGITUDE
        ):
            return True
        return False

    @staticmethod
    def _valid_api_key(api_key: str) -> bool:
        """Return True if API key is valid."""
        if isinstance(api_key, str) and len(api_key) == MAX_API_KEY_LENGTH:
            return True

        return False

    @staticmethod
    def _construct_url(arg: str, **kwargs: str) -> str:
        """Construct AccuWeather API URL."""
        return ENDPOINT + URLS[arg].format(**kwargs)

    @staticmethod
    def _parse_forecast_hourly(
        data: list[dict[str, Any]], to_remove: tuple[str, ...]
    ) -> list[dict[str, Any]]:
        """Parse and clean hourly forecast API response."""
        return [
            {key: value for key, value in item.items() if key not in to_remove}
            for item in data
        ]

    async def _async_get_data(self, url: str) -> Any:
        """Retrieve data from AccuWeather API."""
        async with self._session.get(url, headers=HTTP_HEADERS) as resp:
            if resp.status == HTTPStatus.UNAUTHORIZED.value:
                raise InvalidApiKeyError("Invalid API key")

            if resp.status != HTTPStatus.OK.value:
                error_text = orjson.loads(await resp.text())
                if error_text["Message"] == REQUESTS_EXCEEDED:
                    raise RequestsExceededError(
                        "The allowed number of requests has been exceeded"
                    )
                raise ApiError(f"Invalid response from AccuWeather API: {resp.status}")

            _LOGGER.debug("Data retrieved from %s, status: %s", url, resp.status)
            data = await resp.json()

        if resp.headers["RateLimit-Remaining"].isdigit():
            self._requests_remaining = int(resp.headers["RateLimit-Remaining"])

        if "hourly" in url:
            return data

        return data if isinstance(data, dict) else data[0]

    async def async_get_location(self) -> None:
        """Retrieve location data from AccuWeather."""
        url = self._construct_url(
            ATTR_GEOPOSITION,
            api_key=self._api_key,
            lat=str(self.latitude),
            lon=str(self.longitude),
        )
        data = await self._async_get_data(url)
        self._location_key = data["Key"]
        self._location_name = data["LocalizedName"]

    async def async_get_current_conditions(self) -> CurrentCondition:
        """Retrieve current conditions data from AccuWeather."""
        if not self._location_key:
            await self.async_get_location()

        if TYPE_CHECKING:
            assert self._location_key is not None  # noqa: S101

        url = self._construct_url(
            ATTR_CURRENT_CONDITIONS,
            api_key=self._api_key,
            location_key=self._location_key,
        )
        data = await self._async_get_data(url)

        return CurrentCondition(
            apparent_temperature=Value(
                data["ApparentTemperature"][self.unit_system]["Value"],
                data["ApparentTemperature"][self.unit_system]["UnitType"],
            ),
            ceiling=Value(
                data["Ceiling"][self.unit_system]["Value"],
                data["Ceiling"][self.unit_system]["UnitType"],
            ),
            cloud_cover=Value(data["CloudCover"], UNIT_PERCENTAGE),
            date=datetime.fromisoformat(data["LocalObservationDateTime"]),
            date_epoch=data["EpochTime"],
            dew_point=Value(
                data["DewPoint"][self.unit_system]["Value"],
                data["DewPoint"][self.unit_system]["UnitType"],
            ),
            indoor_relative_humidity=Value(
                data["IndoorRelativeHumidity"], UNIT_PERCENTAGE
            ),
            is_day_time=data["IsDayTime"],
            precipitation_past_hour=Value(
                data["PrecipitationSummary"]["PastHour"][self.unit_system]["Value"],
                data["PrecipitationSummary"]["PastHour"][self.unit_system]["UnitType"],
            ),
            precipitation_type=data["PrecipitationType"].lower()
            if data["HasPrecipitation"]
            else None,
            pressure=Value(
                data["Pressure"][self.unit_system]["Value"],
                data["Pressure"][self.unit_system]["UnitType"],
                data["PressureTendency"]["LocalizedText"],
            ),
            real_feel_temperature=Value(
                data["RealFeelTemperature"][self.unit_system]["Value"],
                data["RealFeelTemperature"][self.unit_system]["UnitType"],
                data["RealFeelTemperature"][self.unit_system]["Phrase"],
            ),
            real_feel_temperature_shade=Value(
                data["RealFeelTemperatureShade"][self.unit_system]["Value"],
                data["RealFeelTemperatureShade"][self.unit_system]["UnitType"],
                data["RealFeelTemperatureShade"][self.unit_system]["Phrase"],
            ),
            relative_humidity=Value(data["RelativeHumidity"], UNIT_PERCENTAGE),
            temperature=Value(
                data["Temperature"][self.unit_system]["Value"],
                data["Temperature"][self.unit_system]["UnitType"],
            ),
            uv_index=data["UVIndex"],
            uv_index_text=data["UVIndexText"].lower(),
            visibility=Value(
                data["Visibility"][self.unit_system]["Value"],
                data["Visibility"][self.unit_system]["UnitType"],
            ),
            weather_text=data["WeatherText"].lower(),
            weather_icon=data["WeatherIcon"],
            wet_bulb_temperature=Value(
                data["WetBulbTemperature"][self.unit_system]["Value"],
                data["WetBulbTemperature"][self.unit_system]["UnitType"],
            ),
            wind_chill_temperature=Value(
                data["WindChillTemperature"][self.unit_system]["Value"],
                data["WindChillTemperature"][self.unit_system]["UnitType"],
            ),
            wind_direction=data["Wind"]["Direction"]["Degrees"],
            wind_gust=Value(
                data["WindGust"]["Speed"][self.unit_system]["Value"],
                data["WindGust"]["Speed"][self.unit_system]["UnitType"],
            ),
            wind_speed=Value(
                data["Wind"]["Speed"][self.unit_system]["Value"],
                data["Wind"]["Speed"][self.unit_system]["UnitType"],
            ),
        )

    async def async_get_forecast(self, metric: bool = True) -> list[ForecastDay]:
        """Retrieve daily forecast data from AccuWeather."""
        if not self._location_key:
            await self.async_get_location()

        if TYPE_CHECKING:
            assert self._location_key is not None  # noqa: S101

        url = self._construct_url(
            ATTR_FORECAST_DAILY_5,
            api_key=self._api_key,
            location_key=self._location_key,
            metric=str(metric),
        )
        data = await self._async_get_data(url)
        forecast = []
        for day in data["DailyForecasts"]:
            forecast.append(
                ForecastDay(
                    cloud_cover_day=Value(day["Day"]["CloudCover"], UNIT_PERCENTAGE),
                    cloud_cover_night=Value(
                        day["Night"]["CloudCover"], UNIT_PERCENTAGE
                    ),
                    date=datetime.fromisoformat(day["Date"]),
                    date_epoch=day["EpochDate"],
                    precipitation_ice_day=Value(
                        day["Day"]["Ice"]["Value"], day["Day"]["Ice"]["UnitType"]
                    ),
                    precipitation_ice_night=Value(
                        day["Night"]["Ice"]["Value"], day["Night"]["Ice"]["UnitType"]
                    ),
                    precipitation_liquid_day=Value(
                        day["Day"]["TotalLiquid"]["Value"],
                        day["Day"]["TotalLiquid"]["UnitType"],
                    ),
                    precipitation_liquid_night=Value(
                        day["Night"]["TotalLiquid"]["Value"],
                        day["Night"]["TotalLiquid"]["UnitType"],
                    ),
                    precipitation_probability_day=Value(
                        day["Day"]["PrecipitationProbability"], UNIT_PERCENTAGE
                    ),
                    precipitation_probability_night=Value(
                        day["Night"]["PrecipitationProbability"], UNIT_PERCENTAGE
                    ),
                    precipitation_rain_day=Value(
                        day["Day"]["Rain"]["Value"], day["Day"]["Rain"]["UnitType"]
                    ),
                    precipitation_rain_night=Value(
                        day["Night"]["Rain"]["Value"], day["Night"]["Rain"]["UnitType"]
                    ),
                    precipitation_snow_day=Value(
                        day["Day"]["Snow"]["Value"], day["Day"]["Snow"]["UnitType"]
                    ),
                    precipitation_snow_night=Value(
                        day["Night"]["Snow"]["Value"], day["Night"]["Snow"]["UnitType"]
                    ),
                    real_feel_temperature_max=Value(
                        day["RealFeelTemperature"]["Maximum"]["Value"],
                        day["RealFeelTemperature"]["Maximum"]["UnitType"],
                        day["RealFeelTemperature"]["Maximum"]["Phrase"],
                    ),
                    real_feel_temperature_min=Value(
                        day["RealFeelTemperature"]["Minimum"]["Value"],
                        day["RealFeelTemperature"]["Minimum"]["UnitType"],
                        day["RealFeelTemperature"]["Minimum"]["Phrase"],
                    ),
                    real_feel_temperature_shade_max=Value(
                        day["RealFeelTemperatureShade"]["Maximum"]["Value"],
                        day["RealFeelTemperatureShade"]["Maximum"]["UnitType"],
                        day["RealFeelTemperatureShade"]["Maximum"]["Phrase"],
                    ),
                    real_feel_temperature_shade_min=Value(
                        day["RealFeelTemperatureShade"]["Minimum"]["Value"],
                        day["RealFeelTemperatureShade"]["Minimum"]["UnitType"],
                        day["RealFeelTemperatureShade"]["Minimum"]["Phrase"],
                    ),
                    temperature_max=Value(
                        day["Temperature"]["Maximum"]["Value"],
                        day["Temperature"]["Maximum"]["UnitType"],
                    ),
                    temperature_min=Value(
                        day["Temperature"]["Minimum"]["Value"],
                        day["Temperature"]["Minimum"]["UnitType"],
                    ),
                    uv_index=self._get_pollen(day["AirAndPollen"], "UVIndex")["Value"],
                    uv_index_text=self._get_pollen(day["AirAndPollen"], "UVIndex")[
                        "Category"
                    ],
                    weather_icon_day=day["Day"]["Icon"],
                    weather_icon_night=day["Night"]["Icon"],
                    weather_text_day=day["Day"]["IconPhrase"].lower(),
                    weather_text_night=day["Night"]["IconPhrase"].lower(),
                    wind_direction_day=Value(
                        day["Day"]["Wind"]["Direction"]["Degrees"],
                        UNIT_DEGREES,
                        day["Day"]["Wind"]["Direction"]["Localized"],
                    ),
                    wind_direction_night=Value(
                        day["Night"]["Wind"]["Direction"]["Degrees"],
                        UNIT_DEGREES,
                        day["Night"]["Wind"]["Direction"]["Localized"],
                    ),
                    wind_gust_day=Value(
                        day["Day"]["WindGust"]["Speed"]["Value"],
                        day["Day"]["WindGust"]["Speed"]["UnitType"],
                    ),
                    wind_gust_night=Value(
                        day["Night"]["WindGust"]["Speed"]["Value"],
                        day["Night"]["WindGust"]["Speed"]["UnitType"],
                    ),
                    wind_speed_day=Value(
                        day["Day"]["Wind"]["Speed"]["Value"],
                        day["Day"]["Wind"]["Speed"]["UnitType"],
                    ),
                    wind_speed_night=Value(
                        day["Night"]["Wind"]["Speed"]["Value"],
                        day["Night"]["Wind"]["Speed"]["UnitType"],
                    ),
                )
            )

        return forecast

    async def async_get_forecast_hourly(
        self, metric: bool = True
    ) -> list[dict[str, Any]]:
        """Retrieve hourly forecast data from AccuWeather."""
        if not self._location_key:
            await self.async_get_location()

        if TYPE_CHECKING:
            assert self._location_key is not None  # noqa: S101

        url = self._construct_url(
            ATTR_FORECAST_HOURLY_12,
            api_key=self._api_key,
            location_key=self._location_key,
            metric=str(metric),
        )
        data = await self._async_get_data(url)
        return self._parse_forecast_hourly(data, REMOVE_FROM_FORECAST)

    @property
    def location_name(self) -> str | None:
        """Return location name."""
        return self._location_name

    @property
    def location_key(self) -> str | None:
        """Return location key."""
        return self._location_key

    @property
    def requests_remaining(self) -> int | None:
        """Return number of remaining allowed requests."""
        return self._requests_remaining

    @staticmethod
    def _get_pollen(pollen_list: list[dict[str, Any]], name: str) -> dict[str, Any]:
        """Return exact pollen dict."""
        for item in pollen_list:
            if item["Name"] == name:
                return item

        return {"Value": None, "Category": None}
