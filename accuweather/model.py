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

    unit_type: int
    value: float
    text: str | None = None

    unit: str | None = None

    def __post_init__(self) -> None:
        """Post init."""
        self.unit = UNIT_MAP.get(self.unit_type)


@dataclass
class CurrentCondition(AccuWeatherData):
    """CurrentCondition class."""

    dew_point: Value
    indoor_relative_humidity: Value
    is_day_time: bool
    local_observation: datetime
    real_feel_temperature_shade: Value
    real_feel_temperature: Value
    relative_humidity: Value
    temperature: Value
    weather_icon: int
    weather_text: str
    wind_direction: int
    wind_gust: Value
    wind_speed: Value
    uv_index: int
    uv_index_text: str
    visibility: Value
    ceiling: Value
    pressure: Value
    apparent_temperature: Value
    wind_chill_temperature: Value
    wet_bulb_temperature: Value
    cloud_cover: Value
    precipitation_past_hour: Value
    precipitation_type: str | None
