import requests
import os
from fastapi import Depends
from fastapi.responses import JSONResponse
from .auth_route_dependency import authenticate_request
from .utils import convert_unix_to_datetime


def get_weather(location, start_date, end_date, is_historical):
    """
    Calls the weather api.

    :param location: The location of interest.
    :type location: str
    :param start_date: The start of the date range.
    :type start_date: int
    :param end_date: The end of the date range.
    :type end_date: int
    :param is_historical: Is the date range in the past (True).
    :type is_historical: bool
    :return: A JSONResponse containing the temperature and weather description for the middle of the date range.
            204 will be returned if there is no content, else 200.
    :rtype: JSONResponse

    :raises HTTPException: With status code 500 in an internal error occurred.
    """

    response = None

    start_date_str = convert_unix_to_datetime(start_date)
    end_date_str = convert_unix_to_datetime(end_date)

    if is_historical:
        base_url = 'https://api.weatherbit.io/v2.0/history/hourly'
    else:
        base_url = 'https://api.weatherbit.io/v2.0/forecast/hourly'

    params = {
        'key': os.getenv('WEATHER_API_KEY'),
        'city': location,
        'start_date': start_date_str,
        'end_date': end_date_str
    }

    weather_response = requests.get(base_url, params=params)
    weather_data = weather_response.json()

    if 'data' in weather_data:
        half_way = len(weather_data['data']) // 2
        data = weather_data['data'][half_way]

        content = {
            'temp': data['temp'],
            'description': data['weather']['description']
        }

        response = JSONResponse(content=content, status_code=200)
    else:
        content = {
            'error': 'No weather data available for the given date and location.'
                     'Please note requests cannot be more than 14 days ahead,'
                     'and the location can only be defined with alphabetic or white space chars.'
        }

        response = JSONResponse(content=content, status_code=204)

    return response


def weather_mgr(app, lambda_client):
    """
    Method that defines all weather mgr methods.
    """
    @app.get('/weather-forecast')
    async def get_weather_forcast(location: str, start_date: int, end_date: int, user_id=Depends(authenticate_request)):
        """
        Get gets the weather forcast (future weather data).

        :param location: The location of interest.
        :type location: str
        :param start_date: The start of the date range.
        :type start_date: int
        :param end_date: The end of the date range.
        :type end_date: int
        :return: A JSONResponse containing the temperature and weather description for the middle of the date range.
                204 will be returned if there is no content, else 200.
        :rtype: JSONResponse
        """
        return get_weather(location, start_date, end_date, False)

    @app.get('/weather-history')
    async def get_weather_history(location: str, start_date: int, end_date: int, user_id=Depends(authenticate_request)):
        """
        Get gets the weather history (past weather data).

        :param location: The location of interest.
        :type location: str
        :param start_date: The start of the date range.
        :type start_date: int
        :param end_date: The end of the date range.
        :type end_date: int
        :return: A JSONResponse containing the temperature and weather description for the middle of the date range.
                204 will be returned if there is no content, else 200.
        :rtype: JSONResponse
        """
        return get_weather(location, start_date, end_date, True)
