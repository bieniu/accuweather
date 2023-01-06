"""Accuweather exceptions."""


class AccuweatherError(Exception):
    """Base class for Accuweather errors."""

    def __init__(self, status: str) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status


class ApiError(AccuweatherError):
    """Raised when AccuWeather API request ended in error."""


class InvalidApiKeyError(AccuweatherError):
    """Raised when API Key format is invalid."""


class InvalidCoordinatesError(AccuweatherError):
    """Raised when coordinates are invalid."""


class RequestsExceededError(AccuweatherError):
    """Raised when allowed number of requests has been exceeded."""
