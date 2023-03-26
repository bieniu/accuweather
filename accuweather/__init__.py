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
    ATTR_FORECAST_DAILY,
    ATTR_FORECAST_HOURLY,
    ATTR_GEOPOSITION,
    HTTP_HEADERS,
    LANGUAGE_MAP,
    REQUESTS_EXCEEDED,
    UNIT_DEGREES,
    UNIT_HOUR,
    UNIT_PERCENTAGE,
)
from .exceptions import (
    ApiError,
    InvalidApiKeyError,
    InvalidCoordinatesError,
    RequestsExceededError,
)
from .model import CurrentCondition, ForecastDay, ForecastHour, Value
from .utils import _construct_url, _get_pollutant, _valid_api_key, _valid_coordinates

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
        language: str = "en",
    ) -> None:
        """Initialize."""
        if not _valid_api_key(api_key):
            raise InvalidApiKeyError(
                "Your API Key must be a 32-character hexadecimal string"
            )
        if not location_key and not _valid_coordinates(latitude, longitude):
            raise InvalidCoordinatesError("Your coordinates are invalid")

        self.latitude = latitude
        self.longitude = longitude
        self._api_key = api_key
        self._session = session
        self._location_key = location_key
        self._location_name: str | None = None
        self._requests_remaining: int | None = None
        self.metric = metric
        self.language = LANGUAGE_MAP.get(language, "en-us")

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

        return data

    async def async_get_location(self) -> None:
        """Retrieve location data from AccuWeather."""
        url = _construct_url(
            ATTR_GEOPOSITION,
            api_key=self._api_key,
            lat=str(self.latitude),
            lon=str(self.longitude),
            language=self.language,
        )
        data = await self._async_get_data(url)
        self._location_key = data["Key"]
        self._location_name = data["LocalizedName"]

    async def async_get_current_conditions(self) -> CurrentCondition:
        """Retrieve current conditions data from AccuWeather."""
        unit_system: str = "Metric" if self.metric else "Imperial"

        if not self._location_key:
            await self.async_get_location()

        if TYPE_CHECKING:
            assert self._location_key is not None  # noqa: S101

        url = _construct_url(
            ATTR_CURRENT_CONDITIONS,
            api_key=self._api_key,
            location_key=self._location_key,
            language=self.language,
        )
        data = (await self._async_get_data(url))[0]

        return CurrentCondition(
            apparent_temperature=Value(
                data["ApparentTemperature"][unit_system]["Value"],
                data["ApparentTemperature"][unit_system]["UnitType"],
            ),
            ceiling=Value(
                data["Ceiling"][unit_system]["Value"],
                data["Ceiling"][unit_system]["UnitType"],
            ),
            cloud_cover=Value(data["CloudCover"], UNIT_PERCENTAGE),
            date_time=datetime.fromisoformat(data["LocalObservationDateTime"]),
            date_time_epoch=data["EpochTime"],
            dew_point=Value(
                data["DewPoint"][unit_system]["Value"],
                data["DewPoint"][unit_system]["UnitType"],
            ),
            has_precipitation=data["HasPrecipitation"],
            indoor_relative_humidity=Value(
                data["IndoorRelativeHumidity"], UNIT_PERCENTAGE
            ),
            is_day_time=data["IsDayTime"],
            precipitation_past_12_hours=Value(
                data["PrecipitationSummary"]["Past12Hours"][unit_system]["Value"],
                data["PrecipitationSummary"]["Past12Hours"][unit_system]["UnitType"],
            ),
            precipitation_past_18_hours=Value(
                data["PrecipitationSummary"]["Past18Hours"][unit_system]["Value"],
                data["PrecipitationSummary"]["Past18Hours"][unit_system]["UnitType"],
            ),
            precipitation_past_24_hours=Value(
                data["PrecipitationSummary"]["Past24Hours"][unit_system]["Value"],
                data["PrecipitationSummary"]["Past24Hours"][unit_system]["UnitType"],
            ),
            precipitation_past_3_hours=Value(
                data["PrecipitationSummary"]["Past3Hours"][unit_system]["Value"],
                data["PrecipitationSummary"]["Past3Hours"][unit_system]["UnitType"],
            ),
            precipitation_past_6_hours=Value(
                data["PrecipitationSummary"]["Past6Hours"][unit_system]["Value"],
                data["PrecipitationSummary"]["Past6Hours"][unit_system]["UnitType"],
            ),
            precipitation_past_9_hours=Value(
                data["PrecipitationSummary"]["Past9Hours"][unit_system]["Value"],
                data["PrecipitationSummary"]["Past9Hours"][unit_system]["UnitType"],
            ),
            precipitation_past_hour=Value(
                data["PrecipitationSummary"]["PastHour"][unit_system]["Value"],
                data["PrecipitationSummary"]["PastHour"][unit_system]["UnitType"],
            ),
            precipitation_type=data["PrecipitationType"].lower()
            if data["HasPrecipitation"]
            else None,
            pressure=Value(
                data["Pressure"][unit_system]["Value"],
                data["Pressure"][unit_system]["UnitType"],
                data["PressureTendency"]["LocalizedText"],
            ),
            real_feel_temperature=Value(
                data["RealFeelTemperature"][unit_system]["Value"],
                data["RealFeelTemperature"][unit_system]["UnitType"],
                data["RealFeelTemperature"][unit_system]["Phrase"],
            ),
            real_feel_temperature_shade=Value(
                data["RealFeelTemperatureShade"][unit_system]["Value"],
                data["RealFeelTemperatureShade"][unit_system]["UnitType"],
                data["RealFeelTemperatureShade"][unit_system]["Phrase"],
            ),
            relative_humidity=Value(data["RelativeHumidity"], UNIT_PERCENTAGE),
            temperature=Value(
                data["Temperature"][unit_system]["Value"],
                data["Temperature"][unit_system]["UnitType"],
            ),
            uv_index=Value(value=data["UVIndex"], text=data["UVIndexText"]),
            visibility=Value(
                data["Visibility"][unit_system]["Value"],
                data["Visibility"][unit_system]["UnitType"],
            ),
            weather_text=data["WeatherText"].lower(),
            weather_icon=data["WeatherIcon"],
            wet_bulb_temperature=Value(
                data["WetBulbTemperature"][unit_system]["Value"],
                data["WetBulbTemperature"][unit_system]["UnitType"],
            ),
            wind_chill_temperature=Value(
                data["WindChillTemperature"][unit_system]["Value"],
                data["WindChillTemperature"][unit_system]["UnitType"],
            ),
            wind_direction=Value(
                data["Wind"]["Direction"]["Degrees"],
                99,
                data["Wind"]["Direction"]["Localized"],
            ),
            wind_gust=Value(
                data["WindGust"]["Speed"][unit_system]["Value"],
                data["WindGust"]["Speed"][unit_system]["UnitType"],
            ),
            wind_speed=Value(
                data["Wind"]["Speed"][unit_system]["Value"],
                data["Wind"]["Speed"][unit_system]["UnitType"],
            ),
        )

    async def async_get_daily_forecast(self, days: int = 5) -> list[ForecastDay]:
        """Retrieve daily forecast data from AccuWeather."""
        forecast = []

        if not self._location_key:
            await self.async_get_location()

        if TYPE_CHECKING:
            assert self._location_key is not None  # noqa: S101

        url = _construct_url(
            ATTR_FORECAST_DAILY,
            days=str(days),
            api_key=self._api_key,
            location_key=self._location_key,
            metric=str(self.metric).lower(),
            language=self.language,
        )
        data = await self._async_get_data(url)

        for day in data["DailyForecasts"]:
            forecast.append(
                ForecastDay(
                    air_quality=_get_pollutant(day["AirAndPollen"], "AirQuality"),
                    cloud_cover_day=Value(day["Day"]["CloudCover"], UNIT_PERCENTAGE),
                    cloud_cover_night=Value(
                        day["Night"]["CloudCover"], UNIT_PERCENTAGE
                    ),
                    date_time_epoch=day["EpochDate"],
                    date_time=datetime.fromisoformat(day["Date"]),
                    grass_pollen=_get_pollutant(day["AirAndPollen"], "Grass"),
                    has_precipitation_day=day["Day"]["HasPrecipitation"],
                    has_precipitation_night=day["Night"]["HasPrecipitation"],
                    hours_of_ice_day=Value(day["Day"]["HoursOfIce"], UNIT_HOUR),
                    hours_of_ice_night=Value(day["Night"]["HoursOfIce"], UNIT_HOUR),
                    hours_of_precipitation_day=Value(
                        day["Day"]["HoursOfPrecipitation"], UNIT_HOUR
                    ),
                    hours_of_precipitation_night=Value(
                        day["Night"]["HoursOfPrecipitation"], UNIT_HOUR
                    ),
                    hours_of_rain_day=Value(day["Day"]["HoursOfRain"], UNIT_HOUR),
                    hours_of_rain_night=Value(day["Night"]["HoursOfRain"], UNIT_HOUR),
                    hours_of_snow_day=Value(day["Day"]["HoursOfSnow"], UNIT_HOUR),
                    hours_of_snow_night=Value(day["Night"]["HoursOfSnow"], UNIT_HOUR),
                    hours_of_sun=Value(day["HoursOfSun"], UNIT_HOUR),
                    ice_probability_day=Value(
                        day["Day"]["IceProbability"], UNIT_PERCENTAGE
                    ),
                    ice_probability_night=Value(
                        day["Night"]["IceProbability"], UNIT_PERCENTAGE
                    ),
                    mold=_get_pollutant(day["AirAndPollen"], "Mold"),
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
                    precipitation_type_day=day["Day"]["PrecipitationType"].lower()
                    if day["Day"]["HasPrecipitation"]
                    else None,
                    precipitation_type_night=day["Night"]["PrecipitationType"].lower()
                    if day["Night"]["HasPrecipitation"]
                    else None,
                    ragweed_pollen=_get_pollutant(day["AirAndPollen"], "Ragweed"),
                    rain_probability_day=Value(
                        day["Day"]["RainProbability"], UNIT_PERCENTAGE
                    ),
                    rain_probability_night=Value(
                        day["Night"]["RainProbability"], UNIT_PERCENTAGE
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
                    snow_probability_day=Value(
                        day["Day"]["SnowProbability"], UNIT_PERCENTAGE
                    ),
                    snow_probability_night=Value(
                        day["Night"]["SnowProbability"], UNIT_PERCENTAGE
                    ),
                    solar_irradiance_day=Value(
                        day["Day"]["SolarIrradiance"]["Value"],
                        day["Day"]["SolarIrradiance"]["UnitType"],
                    ),
                    solar_irradiance_night=Value(
                        day["Night"]["SolarIrradiance"]["Value"],
                        day["Night"]["SolarIrradiance"]["UnitType"],
                    ),
                    thunderstorm_probability_day=Value(
                        day["Day"]["ThunderstormProbability"], UNIT_PERCENTAGE
                    ),
                    thunderstorm_probability_night=Value(
                        day["Night"]["ThunderstormProbability"], UNIT_PERCENTAGE
                    ),
                    temperature_max=Value(
                        day["Temperature"]["Maximum"]["Value"],
                        day["Temperature"]["Maximum"]["UnitType"],
                    ),
                    temperature_min=Value(
                        day["Temperature"]["Minimum"]["Value"],
                        day["Temperature"]["Minimum"]["UnitType"],
                    ),
                    tree_pollen=_get_pollutant(day["AirAndPollen"], "Tree"),
                    uv_index=_get_pollutant(day["AirAndPollen"], "UVIndex"),
                    weather_icon_day=day["Day"]["Icon"],
                    weather_icon_night=day["Night"]["Icon"],
                    weather_text_day=day["Day"]["IconPhrase"].lower(),
                    weather_text_night=day["Night"]["IconPhrase"].lower(),
                    weather_long_text_day=day["Day"]["LongPhrase"].lower(),
                    weather_long_text_night=day["Night"]["LongPhrase"].lower(),
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

    async def async_get_hourly_forecast(self, hours: int = 12) -> list[ForecastHour]:
        """Retrieve hourly forecast data from AccuWeather."""
        forecast = []

        if not self._location_key:
            await self.async_get_location()

        if TYPE_CHECKING:
            assert self._location_key is not None  # noqa: S101

        url = _construct_url(
            ATTR_FORECAST_HOURLY,
            hours=str(hours),
            api_key=self._api_key,
            location_key=self._location_key,
            metric=str(self.metric).lower(),
            language=self.language,
        )
        data = await self._async_get_data(url)

        for hour in data:
            forecast.append(
                ForecastHour(
                    ceiling=Value(
                        hour["Ceiling"]["Value"], hour["Ceiling"]["UnitType"]
                    ),
                    cloud_cover=Value(hour["CloudCover"], UNIT_PERCENTAGE),
                    date_time=datetime.fromisoformat(hour["DateTime"]),
                    date_time_epoch=hour["EpochDateTime"],
                    dew_point=Value(
                        hour["DewPoint"]["Value"], hour["DewPoint"]["UnitType"]
                    ),
                    has_precipitation=hour["HasPrecipitation"],
                    ice_probability=Value(hour["IceProbability"], UNIT_PERCENTAGE),
                    indoor_relative_humidity=Value(
                        hour["RelativeHumidity"], UNIT_PERCENTAGE
                    ),
                    is_daylight=hour["IsDaylight"],
                    precipitation_ice=Value(
                        hour["Ice"]["Value"], hour["Ice"]["UnitType"]
                    ),
                    precipitation_liquid=Value(
                        hour["TotalLiquid"]["Value"],
                        hour["TotalLiquid"]["UnitType"],
                    ),
                    precipitation_probability=Value(
                        hour["PrecipitationProbability"], UNIT_PERCENTAGE
                    ),
                    precipitation_rain=Value(
                        hour["Rain"]["Value"], hour["Rain"]["UnitType"]
                    ),
                    precipitation_snow=Value(
                        hour["Snow"]["Value"], hour["Snow"]["UnitType"]
                    ),
                    precipitation_type=hour["PrecipitationType"].lower()
                    if hour["HasPrecipitation"]
                    else None,
                    rain_probability=Value(hour["RainProbability"], UNIT_PERCENTAGE),
                    real_feel_temperature=Value(
                        hour["RealFeelTemperature"]["Value"],
                        hour["RealFeelTemperature"]["UnitType"],
                        hour["RealFeelTemperature"]["Phrase"],
                    ),
                    real_feel_temperature_shade=Value(
                        hour["RealFeelTemperatureShade"]["Value"],
                        hour["RealFeelTemperatureShade"]["UnitType"],
                        hour["RealFeelTemperatureShade"]["Phrase"],
                    ),
                    relative_humidity=Value(hour["RelativeHumidity"], UNIT_PERCENTAGE),
                    snow_probability=Value(hour["SnowProbability"], UNIT_PERCENTAGE),
                    solar_irradiance=Value(
                        hour["SolarIrradiance"]["Value"],
                        hour["SolarIrradiance"]["UnitType"],
                    ),
                    temperature=Value(
                        hour["Temperature"]["Value"],
                        hour["Temperature"]["UnitType"],
                    ),
                    thunderstorm_probability=Value(
                        hour["ThunderstormProbability"], UNIT_PERCENTAGE
                    ),
                    uv_index=Value(value=hour["UVIndex"], text=hour["UVIndexText"]),
                    visibility=Value(
                        hour["Visibility"]["Value"], hour["Visibility"]["UnitType"]
                    ),
                    weather_icon=hour["WeatherIcon"],
                    weather_text=hour["IconPhrase"].lower(),
                    wet_bulb_temperature=Value(
                        hour["WetBulbTemperature"]["Value"],
                        hour["WetBulbTemperature"]["UnitType"],
                    ),
                    wind_direction=Value(
                        hour["Wind"]["Direction"]["Degrees"],
                        UNIT_DEGREES,
                        hour["Wind"]["Direction"]["Localized"],
                    ),
                    wind_gust=Value(
                        hour["WindGust"]["Speed"]["Value"],
                        hour["WindGust"]["Speed"]["UnitType"],
                    ),
                    wind_speed=Value(
                        hour["Wind"]["Speed"]["Value"],
                        hour["Wind"]["Speed"]["UnitType"],
                    ),
                )
            )

        return forecast

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
