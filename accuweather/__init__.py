"""Python wrapper for getting weather data from AccueWeather API."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

import orjson
from aiohttp import ClientSession

from .const import (
    ATTR_CURRENT_CONDITIONS,
    ATTR_FORECAST_DAILY,
    ATTR_FORECAST_HOURLY,
    ATTR_GEOPOSITION,
    HTTP_HEADERS,
    LANGUAGE_MAP,
    REMOVE_FROM_CURRENT_CONDITION,
    REMOVE_FROM_FORECAST,
    REQUESTS_EXCEEDED,
)
from .exceptions import (
    ApiError,
    InvalidApiKeyError,
    InvalidCoordinatesError,
    RequestsExceededError,
)
from .utils import (
    construct_url,
    parse_current_condition,
    parse_daily_forecast,
    parse_hourly_forecast,
    valid_api_key,
    valid_coordinates,
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
        language: str = "en",
    ) -> None:
        """Initialize."""
        if not valid_api_key(api_key):
            raise InvalidApiKeyError(
                "Your API Key must be a 32-character hexadecimal string"
            )
        if not location_key and not valid_coordinates(latitude, longitude):
            raise InvalidCoordinatesError("Your coordinates are invalid")

        self.latitude = latitude
        self.longitude = longitude
        self.language = LANGUAGE_MAP.get(language, "en-us")
        self._api_key = api_key
        self._session = session
        self._location_key = location_key
        self._location_name: str | None = None
        self._requests_remaining: int | None = None

    async def _async_get_data(self, url: str) -> Any:
        """Retrieve data from AccuWeather API."""
        async with self._session.get(url, headers=HTTP_HEADERS) as resp:
            if resp.status == HTTPStatus.UNAUTHORIZED.value:
                raise InvalidApiKeyError("Invalid API key")

            if resp.status != HTTPStatus.OK.value:
                try:
                    error_text = orjson.loads(await resp.text())
                except orjson.JSONDecodeError as exc:
                    raise ApiError(f"Can't decode API response: {exc}") from exc
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
        url = construct_url(
            ATTR_GEOPOSITION,
            api_key=self._api_key,
            lat=str(self.latitude),
            lon=str(self.longitude),
            language=self.language,
        )
        data = await self._async_get_data(url)
        self._location_key = data["Key"]
        self._location_name = data["LocalizedName"]

    async def async_get_current_conditions(self) -> dict[str, Any]:
        """Retrieve current conditions data from AccuWeather."""
        if not self._location_key:
            await self.async_get_location()

        if TYPE_CHECKING:
            assert self._location_key is not None

        url = construct_url(
            ATTR_CURRENT_CONDITIONS,
            api_key=self._api_key,
            location_key=self._location_key,
            language=self.language,
        )
        data = await self._async_get_data(url)
        return parse_current_condition(data, REMOVE_FROM_CURRENT_CONDITION)

    async def async_get_daily_forecast(
        self, days: int = 5, metric: bool = True
    ) -> list[dict[str, Any]]:
        """Retrieve daily forecast data from AccuWeather."""
        if not self._location_key:
            await self.async_get_location()

        if TYPE_CHECKING:
            assert self._location_key is not None

        url = construct_url(
            ATTR_FORECAST_DAILY,
            api_key=self._api_key,
            location_key=self._location_key,
            days=str(days),
            metric=str(metric).lower(),
            language=self.language,
        )
        data = await self._async_get_data(url)
        return parse_daily_forecast(data, REMOVE_FROM_FORECAST)

    async def async_get_hourly_forecast(
        self, hours: int = 12, metric: bool = True
    ) -> list[dict[str, Any]]:
        """Retrieve hourly forecast data from AccuWeather."""
        if not self._location_key:
            await self.async_get_location()

        if TYPE_CHECKING:
            assert self._location_key is not None

        url = construct_url(
            ATTR_FORECAST_HOURLY,
            api_key=self._api_key,
            location_key=self._location_key,
            hours=str(hours),
            metric=str(metric).lower(),
            language=self.language,
        )
        data = await self._async_get_data(url)
        return parse_hourly_forecast(data, REMOVE_FROM_FORECAST)

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
