import asyncio
import accuweather
from aiohttp import ClientError, ClientSession

MY_API_KEY = 'NLBCJPGTFLZm2NGNsUWRG4cUwojavhb5'

async def main():
    async with ClientSession() as session:
        aw = accuweather.AccuWeather(MY_API_KEY, session, latitude=50.18, longitude=6.28)
        forecast = await aw.async_get_forecast(metric=True)
        key1='Date'
        key2='TemperatureMax'
        for fc in forecast:
            print(fc[key1], fc[key2]['Value'])


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
