"""Utils for AccuWeather."""
from __future__ import annotations

from typing import Any

from .const import (
    ENDPOINT,
    MAX_API_KEY_LENGTH,
    MAX_LATITUDE,
    MAX_LONGITUDE,
    UNIT_PPM3,
    URLS,
)
from .model import Value


def _valid_api_key(api_key: str) -> bool:
    """Return True if API key is valid."""
    if isinstance(api_key, str) and len(api_key) == MAX_API_KEY_LENGTH:
        return True

    return False


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


def _construct_url(arg: str, **kwargs: str) -> str:
    """Construct AccuWeather API URL."""
    return ENDPOINT + URLS[arg].format(**kwargs)


def _get_pollutant(pollutant_list: list[dict[str, Any]], name: str) -> Value:
    """Return Value object for exact pollutant."""
    unit = UNIT_PPM3 if name in ("Grass", "Mold", "Tree", "Ragweed") else None

    for item in pollutant_list:
        if item["Name"] == name:
            return Value(item["Value"], unit, item["Category"])

    return Value()
