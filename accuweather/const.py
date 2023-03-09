"""Constants for AccuWeather library."""
from __future__ import annotations

ATTR_CURRENT_CONDITIONS: str = "currentconditions"
ATTR_FORECAST_DAILY_5: str = "forecasts"
ATTR_FORECAST_HOURLY_12: str = "forecasts_hourly"
ATTR_GEOPOSITION: str = "geoposition"

MAX_API_KEY_LENGTH = 32
MAX_LATITUDE = 90
MAX_LONGITUDE = 180

ENDPOINT: str = "https://dataservice.accuweather.com/"
HTTP_HEADERS: dict[str, str] = {"Content-Encoding": "gzip"}
REQUESTS_EXCEEDED: str = "The allowed number of requests has been exceeded."

REMOVE_FROM_CURRENT_CONDITION: tuple[str, ...] = (
    "LocalObservationDateTime",
    "EpochTime",
    "WeatherText",
    "IsDayTime",
    "TemperatureSummary",
    "MobileLink",
    "Link",
)
REMOVE_FROM_FORECAST: tuple[str, ...] = ("Sun", "Moon", "Sources", "MobileLink", "Link")
TEMPERATURES: tuple[str, ...] = (
    "Temperature",
    "RealFeelTemperature",
    "RealFeelTemperatureShade",
)
URLS: dict[str, str] = {
    ATTR_GEOPOSITION: "locations/v1/cities/geoposition/search?apikey={api_key}&q={lat}%2C{lon}",
    ATTR_CURRENT_CONDITIONS: "currentconditions/v1/{location_key}?apikey={api_key}&details=true",
    ATTR_FORECAST_DAILY_5: "forecasts/v1/daily/5day/{location_key}?apikey={api_key}&details=true&metric={metric}",
    ATTR_FORECAST_HOURLY_12: "forecasts/v1/hourly/12hour/{location_key}?apikey={api_key}&details=true&metric={metric}",
}
