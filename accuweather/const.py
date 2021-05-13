"""Constants for AccuWeather library."""
from typing import Dict, Tuple

ATTR_CURRENT_CONDITIONS: str = "currentconditions"
ATTR_FORECAST: str = "forecasts"
ATTR_GEOPOSITION: str = "geoposition"

ENDPOINT: str = "https://dataservice.accuweather.com/"
HTTP_OK: int = 200
HTTP_UNAUTHORIZED: int = 401
HTTP_HEADERS: Dict[str, str] = {"Content-Encoding": "gzip"}
REQUESTS_EXCEEDED: str = "The allowed number of requests has been exceeded."

REMOVE_FROM_CURRENT_CONDITION: Tuple[str, ...] = (
    "LocalObservationDateTime",
    "EpochTime",
    "WeatherText",
    "IsDayTime",
    "TemperatureSummary",
    "MobileLink",
    "Link",
)
REMOVE_FROM_FORECAST: Tuple[str, ...] = ("Sun", "Moon", "Sources", "MobileLink", "Link")
TEMPERATURES: Tuple[str, ...] = (
    "Temperature",
    "RealFeelTemperature",
    "RealFeelTemperatureShade",
)
URLS: Dict[str, str] = {
    ATTR_GEOPOSITION: "locations/v1/cities/geoposition/search?apikey={api_key}&q={lat}%2C{lon}",
    ATTR_CURRENT_CONDITIONS: "currentconditions/v1/{location_key}?apikey={api_key}&details=true",
    ATTR_FORECAST: "forecasts/v1/daily/5day/{location_key}?apikey={api_key}&details=true&metric={metric}",  # pylint: disable=line-too-long
}
