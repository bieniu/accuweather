[![GitHub Release][releases-shield]][releases]
[![PyPI][pypi-releases-shield]][pypi-releases]
[![PyPI - Downloads][pypi-downloads]][pypi-statistics]
[![Buy me a coffee][buy-me-a-coffee-shield]][buy-me-a-coffee]
[![PayPal_Me][paypal-me-shield]][paypal-me]

# accuweather

Python wrapper for getting weather data from AccuWeather servers.


## API key

To generate API key go to https://developer.accuweather.com/user/register and after registration create an app.


## How to use package
```python
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

```

[releases]: https://github.com/bieniu/accuweather/releases
[releases-shield]: https://img.shields.io/github/release/bieniu/accuweather.svg?style=popout
[pypi-releases]: https://pypi.org/project/accuweather/
[pypi-statistics]: https://pypistats.org/packages/accuweather
[pypi-releases-shield]: https://img.shields.io/pypi/v/accuweather
[pypi-downloads]: https://img.shields.io/pypi/dm/accuweather
[buy-me-a-coffee-shield]: https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white
[buy-me-a-coffee]: https://www.buymeacoffee.com/QnLdxeaqO
[paypal-me-shield]: https://img.shields.io/static/v1.svg?label=%20&message=PayPal.Me&logo=paypal
[paypal-me]: https://www.paypal.me/bieniu79
