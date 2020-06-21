"""
Python wrapper for getting weather data from AccueWeather.
"""
import logging

from aiohttp import ClientSession

from .const import (
    ATTR_CURRENT_CONDITIONS,
    ATTR_FORECAST,
    ATTR_GEOPOSITION,
    ENDPOINT,
    HTTP_HEADERS,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    URLS,
)

_LOGGER = logging.getLogger(__name__)


class AccuWeather:
    """Main class to perform AccuWeather API requests"""

    def __init__(  # pylint:disable=too-many-arguments
        self,
        api_key,
        session: ClientSession,
        latitude=None,
        longitude=None,
        location_key=None,
    ):
        """Initialize."""
        try:
            assert isinstance(api_key, str)
            assert len(api_key) == 32
        except AssertionError:
            raise InvalidApiKeyError(
                "Your API Key must be a 32-character hexadecimal string"
            )

        if not location_key:
            try:
                assert isinstance(latitude, (int, float)) and isinstance(
                    longitude, (int, float)
                )
            except AssertionError:
                raise ValueError
            try:
                assert abs(latitude) <= 90 and abs(longitude) <= 180
            except AssertionError:
                raise InvalidCoordinatesError("Your coordinates are invalid")

        self.latitude = latitude
        self.longitude = longitude
        self._api_key = api_key
        self._session = session
        self._location_key = location_key
        self._location_name = None
        self._requests_remaining = None

    @staticmethod
    def _construct_url(arg: str, **kwargs) -> str:
        """Construct AccuWeather API URL."""
        url = ENDPOINT + URLS[arg].format(**kwargs)
        return url

    async def _async_get_data(self, url: str) -> str:
        """Retreive data from AccuWeather API."""
        async with self._session.get(url, headers=HTTP_HEADERS) as resp:
            if resp.status == HTTP_UNAUTHORIZED:
                _LOGGER.error(
                    "Invalid API key, response from AccuWeather API: %s", resp.status
                )
                raise InvalidApiKeyError(resp.status)
            if resp.status != HTTP_OK:
                _LOGGER.warning(
                    "Invalid response from AccuWeather API: %s", resp.status
                )
                raise ApiError(resp.status)
            _LOGGER.debug("Data retrieved from %s, status: %s", url, resp.status)
            data = await resp.json()
        self._requests_remaining = resp.headers["RateLimit-Remaining"]
        return data

    async def async_get_location(self):
        """Retreive location data from AccuWeather."""
        url = self._construct_url(
            ATTR_GEOPOSITION,
            api_key=self._api_key,
            lat=str(self.latitude),
            lon=str(self.longitude),
        )
        data = await self._async_get_data(url)
        self._location_key = data["Key"]
        self._location_name = data["LocalizedName"]

    async def async_get_current_conditions(self):
        """Retreive current conditions data from AccuWeather."""
        if not self._location_key:
            await self.async_get_location()
        url = self._construct_url(
            ATTR_CURRENT_CONDITIONS,
            api_key=self._api_key,
            location_key=self._location_key,
        )
        data = await self._async_get_data(url)
        return data[0]

    async def async_get_forecast(self):
        """Retreive forecast data from AccuWeather."""
        if not self._location_key:
            await self.async_get_location()
        url = self._construct_url(
            ATTR_FORECAST, api_key=self._api_key, location_key=self._location_key,
        )
        data = await self._async_get_data(url)
        return data

    @property
    def location_name(self):
        """Return location name."""
        return self._location_name

    @property
    def location_key(self):
        """Return location key."""
        return self._location_key

    @property
    def requests_remaining(self):
        """Return number of remaining allowed requests."""
        return self._requests_remaining


class ApiError(Exception):
    """Raised when AccuWeather API request ended in error."""

    def __init__(self, status):
        """Initialize."""
        super(ApiError, self).__init__(status)
        self.status = status


class InvalidApiKeyError(Exception):
    """Raised when API Key format is invalid."""

    def __init__(self, status):
        """Initialize."""
        super(InvalidApiKeyError, self).__init__(status)
        self.status = status


class InvalidCoordinatesError(Exception):
    """Raised when coordinates are invalid."""

    def __init__(self, status):
        """Initialize."""
        super(InvalidCoordinatesError, self).__init__(status)
        self.status = status
