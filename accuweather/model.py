"""Type definitions for AccuWeather."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .const import UNIT_MAP


@dataclass
class AccuWeatherData:
    """AccuWeather data class."""


@dataclass
class Value(AccuWeatherData):
    """Value class."""

    value: float | None = None
    unit_type: int | None = None
    text: str | None = None

    unit: str | None = None

    def __post_init__(self) -> None:
        """Post init."""
        self.unit = UNIT_MAP[self.unit_type] if self.unit_type is not None else None
        self.text = self.text.lower() if self.text else None


@dataclass
class CurrentCondition(AccuWeatherData):
    """CurrentCondition class."""

    apparent_temperature: Value
    ceiling: Value
    cloud_cover: Value
    date_time_epoch: int
    date_time: datetime
    dew_point: Value
    has_precipitation: bool
    indoor_relative_humidity: Value
    is_day_time: bool
    precipitation_past_12_hours: Value
    precipitation_past_18_hours: Value
    precipitation_past_24_hours: Value
    precipitation_past_3_hours: Value
    precipitation_past_6_hours: Value
    precipitation_past_9_hours: Value
    precipitation_past_hour: Value
    precipitation_type: str | None
    pressure: Value
    real_feel_temperature_shade: Value
    real_feel_temperature: Value
    relative_humidity: Value
    temperature: Value
    uv_index: Value
    visibility: Value
    weather_icon: int
    weather_text: str
    wet_bulb_temperature: Value
    wind_chill_temperature: Value
    wind_direction: Value
    wind_gust: Value
    wind_speed: Value


@dataclass
class ForecastDay(AccuWeatherData):
    """Forecast per day class."""

    air_quality: Value
    cloud_cover_day: Value
    cloud_cover_night: Value
    date_time_epoch: int
    date_time: datetime
    grass_pollen: Value
    has_precipitation_day: bool
    has_precipitation_night: bool
    hours_of_ice_day: Value
    hours_of_ice_night: Value
    hours_of_precipitation_day: Value
    hours_of_precipitation_night: Value
    hours_of_rain_day: Value
    hours_of_rain_night: Value
    hours_of_snow_day: Value
    hours_of_snow_night: Value
    hours_of_sun: Value
    ice_probability_day: Value
    ice_probability_night: Value
    mold: Value
    precipitation_ice_day: Value
    precipitation_ice_night: Value
    precipitation_liquid_day: Value
    precipitation_liquid_night: Value
    precipitation_probability_day: Value
    precipitation_probability_night: Value
    precipitation_rain_day: Value
    precipitation_rain_night: Value
    precipitation_snow_day: Value
    precipitation_snow_night: Value
    precipitation_type_day: str | None
    precipitation_type_night: str | None
    ragweed_pollen: Value
    rain_probability_day: Value
    rain_probability_night: Value
    real_feel_temperature_max: Value
    real_feel_temperature_min: Value
    real_feel_temperature_shade_max: Value
    real_feel_temperature_shade_min: Value
    snow_probability_day: Value
    snow_probability_night: Value
    solar_irradiance_day: Value
    solar_irradiance_night: Value
    temperature_max: Value
    temperature_min: Value
    thunderstorm_probability_day: Value
    thunderstorm_probability_night: Value
    tree_pollen: Value
    uv_index: Value
    weather_icon_day: int
    weather_icon_night: int
    weather_long_text_day: str
    weather_long_text_night: str
    weather_text_day: str
    weather_text_night: str
    wind_direction_day: Value
    wind_direction_night: Value
    wind_gust_day: Value
    wind_gust_night: Value
    wind_speed_day: Value
    wind_speed_night: Value


@dataclass
class ForecastHour(AccuWeatherData):
    """Forecast per hour class."""

    ceiling: Value
    cloud_cover: Value
    date_time_epoch: int
    date_time: datetime
    dew_point: Value
    has_precipitation: bool
    ice_probability: Value
    indoor_relative_humidity: Value
    is_daylight: bool
    precipitation_ice: Value
    precipitation_liquid: Value
    precipitation_probability: Value
    precipitation_rain: Value
    precipitation_snow: Value
    precipitation_type: str | None
    rain_probability: Value
    real_feel_temperature_shade: Value
    real_feel_temperature: Value
    relative_humidity: Value
    snow_probability: Value
    solar_irradiance: Value
    temperature: Value
    thunderstorm_probability: Value
    uv_index: Value
    visibility: Value
    weather_icon: int
    weather_text: str
    wet_bulb_temperature: Value
    wind_direction: Value
    wind_gust: Value
    wind_speed: Value
