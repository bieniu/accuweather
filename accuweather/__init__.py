"""Python wrapper for getting weather data from AccueWeather for Limited Trial."""

from __future__ import annotations

import json
import logging
from http import HTTPStatus
from typing import Any, Dict, cast

from aiohttp import ClientSession

from .const import (
    ATTR_CURRENT_CONDITIONS,
    ATTR_FORECAST_DAILY_5,
    ATTR_FORECAST_HOURLY_12,
    ATTR_GEOPOSITION,
    ENDPOINT,
    HTTP_HEADERS,
    REMOVE_FROM_CURRENT_CONDITION,
    REMOVE_FROM_FORECAST,
    REQUESTS_EXCEEDED,
    TEMPERATURES,
    URLS,
)

_LOGGER = logging.getLogger(__name__)


class AccuWeather:
    """Main class to perform AccuWeather API requests."""

    def __init__(
        self,
        api_key: str,
        session: ClientSession,
        latitude: float | None = None,
        longitude: float | None = None,
        location_key: str | None = None,
    ):
        """Initialize."""
        if not self._valid_api_key(api_key):
            raise InvalidApiKeyError(
                "Your API Key must be a 32-character hexadecimal string"
            )
        if not location_key:
            if not self._valid_coordinates(latitude, longitude):
                raise InvalidCoordinatesError("Your coordinates are invalid")
        self.latitude = latitude
        self.longitude = longitude
        self._api_key = api_key
        self._session = session
        self._location_key = location_key
        self._location_name: str | None = None
        self._requests_remaining: int | None = None

    @staticmethod
    def _valid_coordinates(
        latitude: float | int | None, longitude: float | int | None
    ) -> bool:
        """Return True if coordinates are valid."""
        if (
            isinstance(latitude, (int, float))
            and isinstance(longitude, (int, float))
            and abs(latitude) <= 90
            and abs(longitude) <= 180
        ):
            return True
        return False

    @staticmethod
    def _valid_api_key(api_key: str) -> bool:
        """Return True if API key is valid."""
        if isinstance(api_key, str) and len(api_key) == 32:
            return True
        return False

    @staticmethod
    def _construct_url(arg: str, **kwargs: str) -> str:
        """Construct AccuWeather API URL."""
        url = ENDPOINT + URLS[arg].format(**kwargs)
        return url

    @staticmethod
    def _clean_current_condition(
        data: dict[str, Any], to_remove: tuple[str, ...]
    ) -> dict[str, Any]:
        """Clean current condition API response."""
        return {key: data[key] for key in data if key not in to_remove}

    @staticmethod
    def _parse_forecast_daily(data: dict, to_remove: tuple) -> list:
        """Parse and clean daily forecast API response."""
        parsed_data = [
            {key: value for key, value in item.items() if key not in to_remove}
            for item in data["DailyForecasts"]
        ]

        for day in parsed_data:
            # For some forecast days, the AccuWeather API does not provide an Ozone value.
            day.setdefault("Ozone", {})
            day["Ozone"].setdefault("Value")
            day["Ozone"].setdefault("Category")

            for item in day["AirAndPollen"]:
                if item["Name"] == "AirQuality":
                    day[item["Type"]] = item
                    day[item["Type"]].pop("Name")
                    day[item["Type"]].pop("Type")
                else:
                    day[item["Name"]] = item
                    day[item["Name"]].pop("Name")
            day.pop("AirAndPollen")

            for temp in TEMPERATURES:
                day[f"{temp}Min"] = day[temp]["Minimum"]
                day[f"{temp}Max"] = day[temp]["Maximum"]
                day.pop(temp)
            for key, value in day["Day"].items():
                day[f"{key}Day"] = value
            day.pop("Day")

            for key, value in day["Night"].items():
                day[f"{key}Night"] = value
            day.pop("Night")
        return parsed_data

    @staticmethod
    def _parse_forecast_hourly(data: dict, to_remove: tuple) -> list:
        """Parse and clean hourly forecast API response."""
        parsed_data = [
            {key: value for key, value in item.items() if key not in to_remove}
            for item in data["HourlyForecast"]
        ]
        return parsed_data

    async def _async_get_data(self, url: str) -> dict[str, Any]:
        """Retrieve data from AccuWeather API."""
        async with self._session.get(url, headers=HTTP_HEADERS) as resp:
            if resp.status == HTTPStatus.UNAUTHORIZED.value:
                raise InvalidApiKeyError("Invalid API key")
            if resp.status != HTTPStatus.OK.value:
                error_text = json.loads(await resp.text())
                if error_text["Message"] == REQUESTS_EXCEEDED:
                    raise RequestsExceededError(
                        "The allowed number of requests has been exceeded"
                    )
                raise ApiError(f"Invalid response from AccuWeather API: {resp.status}")
            _LOGGER.debug("Data retrieved from %s, status: %s", url, resp.status)
            data = await resp.json()
        if resp.headers["RateLimit-Remaining"].isdigit():
            self._requests_remaining = int(resp.headers["RateLimit-Remaining"])

        # nasty hack to account for different data structure returned by hourly forecast API call
        if "hourly" in url:
            data = {"HourlyForecast": data}
        # pylint: disable=deprecated-typing-alias
        return cast(Dict[str, Any], data if isinstance(data, dict) else data[0])

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

    async def async_get_current_conditions(self) -> dict[str, Any]:
        """Retrieve current conditions data from AccuWeather."""
        if not self._location_key:
            await self.async_get_location()
        assert self._location_key is not None
        url = self._construct_url(
            ATTR_CURRENT_CONDITIONS,
            api_key=self._api_key,
            location_key=self._location_key,
        )
        data = await self._async_get_data(url)
        return self._clean_current_condition(data, REMOVE_FROM_CURRENT_CONDITION)

    async def async_get_forecast(self, metric: bool = True) -> list[dict[str, Any]]:
        """Retrieve daily forecast data from AccuWeather."""
        if not self._location_key:
            await self.async_get_location()
        assert self._location_key is not None
        url = self._construct_url(
            ATTR_FORECAST_DAILY_5,
            api_key=self._api_key,
            location_key=self._location_key,
            metric=str(metric),
        )
        data = await self._async_get_data(url)
        return self._parse_forecast_daily(data, REMOVE_FROM_FORECAST)

    async def async_get_forecast_hourly(
        self, metric: bool = True
    ) -> list[dict[str, Any]]:
        """Retrieve hourly forecast data from AccuWeather."""
        if not self._location_key:
            await self.async_get_location()
        assert self._location_key is not None
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


class ApiError(Exception):
    """Raised when AccuWeather API request ended in error."""

    def __init__(self, status: str):
        """Initialize."""
        super().__init__(status)
        self.status = status


class InvalidApiKeyError(Exception):
    """Raised when API Key format is invalid."""

    def __init__(self, status: str):
        """Initialize."""
        super().__init__(status)
        self.status = status


class InvalidCoordinatesError(Exception):
    """Raised when coordinates are invalid."""

    def __init__(self, status: str):
        """Initialize."""
        super().__init__(status)
        self.status = status


class RequestsExceededError(Exception):
    """Raised when allowed number of requests has been exceeded."""

    def __init__(self, status: str):
        """Initialize."""
        super().__init__(status)
        self.status = status
