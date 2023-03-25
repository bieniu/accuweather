"""Utils for AccuWeather."""
from __future__ import annotations

from typing import Any

from .const import MAX_LATITUDE, MAX_LONGITUDE
from .model import Value


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


def _get_pollen(pollen_list: list[dict[str, Any]], name: str) -> Value:
    """Return Value object for exact pollen."""
    for item in pollen_list:
        if item["Name"] == name:
            return Value(value=item["Value"], text=item["Category"])

    return Value()
