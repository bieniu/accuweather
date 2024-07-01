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


def valid_coordinates(latitude: float | None, longitude: float | None) -> bool:
    """Return True if coordinates are valid."""
    return (
        isinstance(latitude, int | float)
        and isinstance(longitude, int | float)
        and abs(latitude) <= MAX_LATITUDE
        and abs(longitude) <= MAX_LONGITUDE
    )


def valid_api_key(api_key: str) -> bool:
    """Return True if API key is valid."""
    return isinstance(api_key, str) and len(api_key) == MAX_API_KEY_LENGTH


def construct_url(arg: str, **kwargs: str) -> str:
    """Construct AccuWeather API URL."""
    return ENDPOINT + URLS[arg].format(**kwargs)


def parse_current_condition(
    data: dict[str, Any], to_remove: tuple[str, ...]
) -> dict[str, Any]:
    """Clean current condition API response."""
    result = {key: data[key] for key in data if key not in to_remove}
    if isinstance(result["PrecipitationType"], str):
        result["PrecipitationType"] = result["PrecipitationType"].lower()
    result["UVIndexText"] = result["UVIndexText"].lower()
    result["PressureTendency"]["LocalizedText"] = result["PressureTendency"][
        "LocalizedText"
    ].lower()
    return result


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
            # Sometimes these values contain a space and an additional description,
            # we do not want that.
            # https://github.com/home-assistant/core/issues/93115
            day[item["Name"]]["Category"] = (
                day[item["Name"]]["Category"].split(" ")[0].lower()
            )
            day[item["Name"]].pop("Name")
        day.pop("AirAndPollen")

        for temp in TEMPERATURES:
            day[f"{temp}Min"] = day[temp]["Minimum"]
            day[f"{temp}Max"] = day[temp]["Maximum"]
            day.pop(temp)

        for item in ("Day", "Night"):
            for key, value in day[item].items():
                if isinstance(value, str) and key not in ("ShortPhrase", "LongPhrase"):
                    day[f"{key}{item}"] = value.lower()
                else:
                    day[f"{key}{item}"] = value
            day.pop(item)

    return parsed_data


def parse_hourly_forecast(
    data: list[dict[str, Any]], to_remove: tuple[str, ...]
) -> list[dict[str, Any]]:
    """Parse and clean hourly forecast API response."""
    result = [
        {key: value for key, value in item.items() if key not in to_remove}
        for item in data
    ]

    for hour in result:
        for key, value in hour.items():
            if isinstance(value, str):
                hour[key] = value.lower()

    return result
