import requests
import json
from config import YANDEX_URL, YANDEX_HEADER
from http_codes import OK

class ForeignApiError(Exception):
    def __init__(self, api_name: str, code: int) -> None:
        super().__init__(f'api {api_name} returned status code {code}')


def get_weather(lat: float, lon: float, key: str) -> dict:
    headers = {YANDEX_HEADER: key}
    params = {'lat': lat, 'lon': lon}
    response = requests.get(YANDEX_URL, headers=headers, params=params)
    if response.status_code == OK:
        weather = json.loads(response.content)
        fact = weather['fact']
        return {key: fact[key] for key in ('temp', 'feels_like', 'wind_speed')}
    raise ForeignApiError('Yandex API', response.status_code)
