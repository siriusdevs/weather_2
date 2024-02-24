HOST = '127.0.0.1'
PORT = 8000

TEMPLATES = 'templates/'
MAIN_TEMPLATE = f'{TEMPLATES}index.html'
WEATHER_TEMPLATE = f'{TEMPLATES}weather.html'
CITIES_TEMPLATES = f'{TEMPLATES}cities.html'

CONTENT_HEADER = 'Content-Type', 'text/html'

YANDEX_URL = 'https://api.weather.yandex.ru/v2/informers'
YANDEX_HEADER = 'X-Yandex-API-Key'

DEFAULT_PG_PORT = 5555
