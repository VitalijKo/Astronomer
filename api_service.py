import aiohttp
import json
import config
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from coordinates import Coordinates


class WindDirection(IntEnum):
    North = 0
    Northeast = 45
    East = 90
    Southeast = 135
    South = 180
    Southwest = 225
    West = 270
    Northwest = 315


@dataclass(frozen=True)
class Weather:
    location: str
    temperature: float
    temperature_feeling: float
    description: str
    wind_speed: float
    wind_direction: str
    sunrise: datetime
    sunset: datetime


async def get_weather(coordinates):
    owm_response = await _get_owm_response(
        longitude=coordinates.longitude,
        latitude=coordinates.latitude
    )

    weather = _parse_owm_response(owm_response)

    return weather


async def _get_owm_response(latitude, longitude):
    url = config.CURRENT_WEATHER_API_CALL.format(latitude=latitude, longitude=longitude)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_text = await response.text()

            return response_text


def _parse_owm_response(owm_response):
    owm_dict = json.loads(owm_response)

    return Weather(
        location=_parse_location(owm_dict),
        temperature=_parse_temperature(owm_dict),
        temperature_feeling=_parse_temperature_feeling(owm_dict),
        description=_parse_description(owm_dict),
        sunrise=_parse_sun_time(owm_dict, 'sunrise'),
        sunset=_parse_sun_time(owm_dict, 'sunset'),
        wind_speed=_parse_wind_speed(owm_dict),
        wind_direction=_parse_wind_direction(owm_dict)
    )


def _parse_location(owm_dict):
    return owm_dict['name']


def _parse_temperature(owm_dict):
    return owm_dict['main']['temp']


def _parse_temperature_feeling(owm_dict):
    return owm_dict['main']['feels_like']


def _parse_description(owm_dict):
    return str(owm_dict['weather'][0]['description']).capitalize()


def _parse_sun_time(owm_dict, time):
    return datetime.fromtimestamp(owm_dict['sys'][time])


def _parse_wind_speed(owm_dict):
    return owm_dict['wind']['speed']


def _parse_wind_direction(owm_dict):
    degrees = owm_dict['wind']['deg']
    degrees = round(degrees / 45) * 45

    if degrees == 360:
        degrees = 0

    return WindDirection(degrees).name
