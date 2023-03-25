"""Utils for AccuWeather."""
from __future__ import annotations

from typing import Any

from .const import ENDPOINT, MAX_API_KEY_LENGTH, MAX_LATITUDE, MAX_LONGITUDE, URLS
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


def _get_pollen(pollen_list: list[dict[str, Any]], name: str) -> Value:
    """Return Value object for exact pollen."""
    for item in pollen_list:
        if item["Name"] == name:
            return Value(value=item["Value"], text=item["Category"])

    return Value()
