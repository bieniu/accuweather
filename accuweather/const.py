"""Constants for AccuWeather library."""
ATTR_CURRENT_CONDITIONS = "currentconditions"
ATTR_FORECASTS = "forecasts"
ATTR_GEOPOSITION = "geoposition"

ENDPOINT = "https://dataservice.accuweather.com/"

HTTP_OK = 200
HTTP_HEADERS = {"Content-Encoding": "gzip"}

URLS = {
    ATTR_GEOPOSITION: "locations/v1/cities/geoposition/search?apikey={api_key}&q={lat}%2C{lon}",
    ATTR_CURRENT_CONDITIONS: "currentconditions/v1/{location_key}?apikey={api_key}&details=true",
    ATTR_FORECASTS: "forecasts/v1/daily/5day/{location_key}?apikey={api_key}&details=true",
}
