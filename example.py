import asyncio
import logging

from aiohttp import ClientError, ClientSession
from accuweather import AccuWeather, ApiError, InvalidApiKeyError, InvalidCoordinatesError

LATITUDE = 52.1201
LONGITUDE = 19.9203
LOCATION_KEY = 264349
API_KEY = "xxxx"

logging.basicConfig(level=logging.DEBUG)

async def main():
    async with ClientSession() as websession:
        try:
            # accuweather = AccuWeather(API_KEY, websession, latitude=LATITUDE, longitude=LONGITUDE)
            accuweather = AccuWeather(API_KEY, websession, location_key=LOCATION_KEY)
            current_conditions = await accuweather.async_get_current_conditions()
            forecasts = await accuweather.async_get_current_conditions()
            print(f"Location: {accuweather.location_name} ({accuweather.location_key})")
            print(f"Requests remaining: {accuweather.requests_remaining}")
            print(f"Current: {current_conditions}")
            print(f"Forecast: {forecasts}")
        except (ApiError, InvalidApiKeyError, InvalidCoordinatesError) as error:
            print(error)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
