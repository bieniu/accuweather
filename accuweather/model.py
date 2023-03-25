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

    value: float
    unit_type: int | None = None
    text: str | None = None

    unit: str | None = None

    def __post_init__(self) -> None:
        """Post init."""
        self.unit = UNIT_MAP.get(self.unit_type) if self.unit_type else None
        self.test = self.text.lower() if self.text else None


@dataclass
class CurrentCondition(AccuWeatherData):
    """CurrentCondition class."""

    apparent_temperature: Value
    ceiling: Value
    cloud_cover: Value
    dew_point: Value
    indoor_relative_humidity: Value
    is_day_time: bool
    date: datetime
    date_epoch: int
    precipitation_past_hour: Value
    precipitation_type: str | None
    pressure: Value
    real_feel_temperature_shade: Value
    real_feel_temperature: Value
    relative_humidity: Value
    temperature: Value
    uv_index_text: str
    uv_index: int
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

    cloud_cover_day: Value
    cloud_cover_night: Value
    date_epoch: int
    date: datetime
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
    real_feel_temperature_max: Value
    real_feel_temperature_min: Value
    real_feel_temperature_shade_max: Value
    real_feel_temperature_shade_min: Value
    temperature_max: Value
    temperature_min: Value
    uv_index: int
    uv_index_text: str
    weather_icon_day: int
    weather_icon_night: int
    weather_text_day: str
    weather_text_night: str
    wind_direction_day: Value
    wind_direction_night: Value
    wind_gust_day: Value
    wind_gust_night: Value
    wind_speed_day: Value
    wind_speed_night: Value
