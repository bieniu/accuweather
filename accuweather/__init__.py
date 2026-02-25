"""Python wrapper for getting weather data from AccueWeather API."""

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

import orjson
from aiohttp import ClientSession
from yarl import URL

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
    clean_url,
    construct_url,
    parse_current_condition,
    parse_daily_forecast,
    parse_hourly_forecast,
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

    def _resolve_language(self, language: str | None) -> str:
        """Resolve language code to AccuWeather format."""
        if language:
            return LANGUAGE_MAP.get(language, "en-us")
        return self.language

    async def _ensure_location_key(self) -> str:
        """Ensure location key is available, fetching it if necessary."""
        if not self._location_key:
            await self.async_get_location()

        if TYPE_CHECKING:
            assert self._location_key is not None

        return self._location_key

    async def _async_get_data(self, url: URL) -> Any:
        """Retrieve data from AccuWeather API."""
        async with self._session.get(url, headers=HTTP_HEADERS) as resp:
            if resp.status in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
                raise InvalidApiKeyError("Invalid API key")

            if resp.status != HTTPStatus.OK:
                try:
                    error_text = orjson.loads(await resp.text())
                except orjson.JSONDecodeError as exc:
                    raise ApiError(f"Can't decode API response: {exc}") from exc
                if error_text.get("Message") == REQUESTS_EXCEEDED:
                    raise RequestsExceededError(
                        "The allowed number of requests has been exceeded"
                    )
                raise ApiError(f"Invalid response from AccuWeather API: {resp.status}")

            _LOGGER.debug(
                "Data retrieved from %s, status: %s", clean_url(url), resp.status
            )
            data = await resp.json()

        if resp.headers["RateLimit-Remaining"].isdigit():
            self._requests_remaining = int(resp.headers["RateLimit-Remaining"])

        if "hourly" in url.path:
            return data

        return data if isinstance(data, dict) else data[0]

    async def async_get_location(self) -> None:
        """Retrieve location data from AccuWeather."""
        url = construct_url(
            ATTR_GEOPOSITION,
            apikey=self._api_key,
            q=f"{self.latitude},{self.longitude}",
            language=self.language,
        )
        data = await self._async_get_data(url)
        self._location_key = data["Key"]
        self._location_name = data["LocalizedName"]

    async def async_get_current_conditions(
        self, language: str | None = None
    ) -> dict[str, Any]:
        """Retrieve current conditions data from AccuWeather."""
        resolved_language = self._resolve_language(language)
        location_key = await self._ensure_location_key()

        url = construct_url(
            ATTR_CURRENT_CONDITIONS,
            apikey=self._api_key,
            location_key=location_key,
            language=resolved_language,
            details=True,
        )
        data = await self._async_get_data(url)
        return parse_current_condition(data, REMOVE_FROM_CURRENT_CONDITION)

    async def async_get_daily_forecast(
        self, days: int = 5, metric: bool = True, language: str | None = None
    ) -> list[dict[str, Any]]:
        """Retrieve daily forecast data from AccuWeather."""
        resolved_language = self._resolve_language(language)
        location_key = await self._ensure_location_key()

        url = construct_url(
            ATTR_FORECAST_DAILY,
            apikey=self._api_key,
            location_key=location_key,
            days=days,
            metric=metric,
            language=resolved_language,
            details=True,
        )
        data = await self._async_get_data(url)
        return parse_daily_forecast(data, REMOVE_FROM_FORECAST)

    async def async_get_hourly_forecast(
        self, hours: int = 12, metric: bool = True, language: str | None = None
    ) -> list[dict[str, Any]]:
        """Retrieve hourly forecast data from AccuWeather."""
        resolved_language = self._resolve_language(language)
        location_key = await self._ensure_location_key()

        url = construct_url(
            ATTR_FORECAST_HOURLY,
            apikey=self._api_key,
            location_key=location_key,
            hours=hours,
            metric=metric,
            language=resolved_language,
            details=True,
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
