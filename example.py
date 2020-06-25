import asyncio
import logging

from accuweather import (
    AccuWeather,
    ApiError,
    InvalidApiKeyError,
    InvalidCoordinatesError,
    RequestsExceededError,
)
from aiohttp import ClientError, ClientSession

LATITUDE = 52.0677904
LONGITUDE = 19.4795644
LOCATION_KEY = "268068"
API_KEY = "xxxxx"

logging.basicConfig(level=logging.DEBUG)


async def main():
    async with ClientSession() as websession:
        try:
            accuweather = AccuWeather(
                API_KEY, websession, latitude=LATITUDE, longitude=LONGITUDE
            )
            current_conditions = await accuweather.async_get_current_conditions()
            forecast = await accuweather.async_get_forecast(metric=True)
        except (
            ApiError,
            InvalidApiKeyError,
            InvalidCoordinatesError,
            ClientError,
            RequestsExceededError,
        ) as error:
            print(f"Error: {error}")

        print(f"Location: {accuweather.location_name} ({accuweather.location_key})")
        print(f"Requests remaining: {accuweather.requests_remaining}")
        print(f"Current: {current_conditions}")
        print(f"Forecast: {forecast}")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
