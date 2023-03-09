"""Type definitions for AccuWeather."""
from __future__ import annotations

from dataclasses import dataclass

from .const import UNIT_MAP


@dataclass
class AccuWeatherData:
    """AccuWeather data class."""


@dataclass
class Value(AccuWeatherData):
    """Value class."""

    unit_int: int
    value: float

    unit: str | None = None

    def __post_init__(self) -> None:
        """Post init."""
        self.unit = UNIT_MAP.get(self.unit_int)


@dataclass
class Temperature(AccuWeatherData):
    """Temperature class."""

    imperial: Value
    metric: Value


@dataclass
class CurrentCondition(AccuWeatherData):
    """CurrentCondition class."""

    temperature: Temperature
    is_day_time: bool
    weather_icon: int
    weather_text: str
