"""Example of usage."""
import asyncio
import logging

from aiohttp import ClientError, ClientSession

from accuweather import AccuWeather
from accuweather.exceptions import AccuweatherError

LATITUDE = 52.0677904
LONGITUDE = 19.4795644
LOCATION_KEY = "268068"
API_KEY = "xxx"

logging.basicConfig(level=logging.DEBUG)


async def main():
    """Run main function."""
    async with ClientSession() as websession:
        try:
            accuweather = AccuWeather(
                API_KEY,
                websession,
                latitude=LATITUDE,
                longitude=LONGITUDE,
                metric=True,
                language="pl",
            )
            current_conditions = await accuweather.async_get_current_conditions()
            forecast = await accuweather.async_get_daily_forecast(days=5)
            forecast_hourly = await accuweather.async_get_hourly_forecast(hours=12)
        except (AccuweatherError, ClientError) as error:
            print(f"Error: {error}")
        else:
            print(f"Location: {accuweather.location_name} ({accuweather.location_key})")
            print(f"Requests remaining: {accuweather.requests_remaining}")
            print(f"Current: {current_conditions}")
            print(f"Forecast: {forecast}")
            print(f"Forecast hourly: {forecast_hourly}")


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
loop.close()
