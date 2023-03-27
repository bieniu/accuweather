"""Constants for AccuWeather library."""
from __future__ import annotations

ATTR_CURRENT_CONDITIONS: str = "currentconditions"
ATTR_FORECAST_DAILY: str = "forecasts"
ATTR_FORECAST_HOURLY: str = "forecasts_hourly"
ATTR_GEOPOSITION: str = "geoposition"

MAX_API_KEY_LENGTH = 32
MAX_LATITUDE = 90
MAX_LONGITUDE = 180

ENDPOINT: str = "https://dataservice.accuweather.com/"
HTTP_HEADERS: dict[str, str] = {"Content-Encoding": "gzip"}
REQUESTS_EXCEEDED: str = "The allowed number of requests has been exceeded."

REMOVE_FROM_FORECAST: tuple[str, ...] = ("Sun", "Moon", "Sources", "MobileLink", "Link")
TEMPERATURES: tuple[str, ...] = (
    "Temperature",
    "RealFeelTemperature",
    "RealFeelTemperatureShade",
)
URLS: dict[str, str] = {
    ATTR_GEOPOSITION: "locations/v1/cities/geoposition/search?apikey={api_key}&q={lat}%2C{lon}&language={language}",
    ATTR_CURRENT_CONDITIONS: "currentconditions/v1/{location_key}?apikey={api_key}&details=true&language={language}",
    ATTR_FORECAST_DAILY: "forecasts/v1/daily/{days}day/{location_key}?apikey={api_key}&details=true&metric={metric}&language={language}",
    ATTR_FORECAST_HOURLY: "forecasts/v1/hourly/{hours}hour/{location_key}?apikey={api_key}&details=true&metric={metric}&language={language}",
}

UNIT_DEGREES: int = 99
UNIT_HOUR: int = 98
UNIT_PERCENTAGE: int = 20
UNIT_PPM3: int = 97

UNIT_MAP: dict[int, str] = {
    0: "ft",
    1: "in",
    2: "mi",
    3: "mm",
    4: "cm",
    5: "m",
    6: "km",
    7: "km/h",
    9: "mi/h",
    12: "inHg",
    14: "mbar",
    17: "°C",
    18: "°F",
    20: "%",
    33: "W/m²",
    97: "p/m³",
    98: "h",
    99: "°",
}

LANGUAGE_MAP: dict[str, str] = {
    "ar": "ar-sa",
    "bg": "bg-bg",
    "bn": "bn-in",
    "ca": "ca-es",
    "cs": "cs-cz",
    "da": "da-dk",
    "de": "de-de",
    "el": "el-gr",
    "en-GB": "en-gb",
    "en": "en-us",
    "es-419": "es-419",
    "es": "es-es",
    "et": "et-ee",
    "fa": "fa-ir",
    "fi": "fi-fi",
    "fr": "fr-fr",
    "he": "he-il",
    "hi": "hi-in",
    "hr": "hr-hr",
    "hu": "hu-hu",
    "id": "id-id",
    "is": "is-is",
    "it": "it-it",
    "ja": "ja-jp",
    "ko": "ko-kr",
    "lt": "lt-lt",
    "lv": "lv-lv",
    "nl": "nl-nl",
    "pl": "pl-pl",
    "pt-BR": "pt-br",
    "pt": "pt-pt",
    "ro": "ro-ro",
    "ru": "ru-ru",
    "sk": "sk-sk",
    "sr-Latn": "sr-latn",
    "sv": "sv-se",
    "ta": "ta-in",
    "te": "te-in",
    "th": "th-th",
    "tr": "tr-tr",
    "uk": "uk-ua",
    "ur": "ur-pk",
    "vi": "vi-vn",
    "zh-Hans": "zh-cn",
    "zh-Hant": "zh-tw",
}
