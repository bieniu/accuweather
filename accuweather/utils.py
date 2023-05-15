"""Utils for AccuWeather."""
from __future__ import annotations

from typing import Any

from .const import (
    ENDPOINT,
    MAX_API_KEY_LENGTH,
    MAX_LATITUDE,
    MAX_LONGITUDE,
    TEMPERATURES,
    URLS,
)


def valid_coordinates(
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


def valid_api_key(api_key: str) -> bool:
    """Return True if API key is valid."""
    if isinstance(api_key, str) and len(api_key) == MAX_API_KEY_LENGTH:
        return True

    return False


def construct_url(arg: str, **kwargs: str) -> str:
    """Construct AccuWeather API URL."""
    return ENDPOINT + URLS[arg].format(**kwargs)


def clean_current_condition(
    data: dict[str, Any], to_remove: tuple[str, ...]
) -> dict[str, Any]:
    """Clean current condition API response."""
    return {key: data[key] for key in data if key not in to_remove}


def parse_daily_forecast(
    data: dict[str, Any], to_remove: tuple[str, ...]
) -> list[dict[str, Any]]:
    """Parse and clean daily forecast API response."""
    parsed_data = [
        {key: value for key, value in item.items() if key not in to_remove}
        for item in data["DailyForecasts"]
    ]

    for day in parsed_data:
        for item in day["AirAndPollen"]:
            day[item["Name"]] = item
            day[item["Name"]]["Category"] = day[item["Name"]]["Category"].lower()
            day[item["Name"]].pop("Name")
        day.pop("AirAndPollen")

        for temp in TEMPERATURES:
            day[f"{temp}Min"] = day[temp]["Minimum"]
            day[f"{temp}Max"] = day[temp]["Maximum"]
            day.pop(temp)

        for key, value in day["Day"].items():
            day[f"{key}Day"] = value
        day.pop("Day")

        for key, value in day["Night"].items():
            day[f"{key}Night"] = value
        day.pop("Night")
    return parsed_data


def parse_hourly_forecast(
    data: list[dict[str, Any]], to_remove: tuple[str, ...]
) -> list[dict[str, Any]]:
    """Parse and clean hourly forecast API response."""
    return [
        {key: value for key, value in item.items() if key not in to_remove}
        for item in data
    ]
