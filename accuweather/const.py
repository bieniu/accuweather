"""Constants for AccuWeather library."""
ATTR_CURRENT_CONDITIONS: str = "currentconditions"
ATTR_FORECAST: str = "forecasts"
ATTR_GEOPOSITION: str = "geoposition"

ENDPOINT: str = "https://dataservice.accuweather.com/"
HTTP_OK: int = 200
HTTP_UNAUTHORIZED: int = 401
HTTP_HEADERS: dict = {"Content-Encoding": "gzip"}
REQUESTS_EXCEEDED: str = "The allowed number of requests has been exceeded."

REMOVE_FROM_CURRENT_CONDITION: tuple = (
    "LocalObservationDateTime",
    "EpochTime",
    "WeatherText",
    "IsDayTime",
    "TemperatureSummary",
    "MobileLink",
    "Link",
)
REMOVE_FROM_FORECAST: tuple = ("Sun", "Moon", "Sources", "MobileLink", "Link")
TEMPERATURES: tuple = ("Temperature", "RealFeelTemperature", "RealFeelTemperatureShade")
URLS: dict = {
    ATTR_GEOPOSITION: "locations/v1/cities/geoposition/search?apikey={api_key}&q={lat}%2C{lon}",
    ATTR_CURRENT_CONDITIONS: "currentconditions/v1/{location_key}?apikey={api_key}&details=true",
    ATTR_FORECAST: "forecasts/v1/daily/5day/{location_key}?apikey={api_key}&details=true&metric={metric}",  # pylint: disable=line-too-long
}
