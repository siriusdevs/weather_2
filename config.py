HOST = '127.0.0.1'
PORT = 8000

TEMPLATES = 'templates/'
MAIN_TEMPLATE = f'{TEMPLATES}index.html'
WEATHER_TEMPLATE = f'{TEMPLATES}weather.html'
CITIES_TEMPLATES = f'{TEMPLATES}cities.html'
WEATHER_DUMMY_TEMPLATE = f'{TEMPLATES}weather_dummy.html'

CONTENT_HEADER = 'Content-Type', 'text/html'
CONTENT_LENGTH = 'Content-Length'
LOCATION_HEADER = 'Content-Location'
KEY_HEADER = 'WEATHER_API_KEY'

YANDEX_URL = 'https://api.weather.yandex.ru/v2/informers'
YANDEX_HEADER = 'X-Yandex-API-Key'

DEFAULT_PG_PORT = 5555
ALLOW_READ = {'Allow': '[GET, HEAD]'}
ALLOW_CHANGE = {'Allow': '[GET, HEAD, POST]'}

CITY_REQUIRED_KEYS = 'name', 'latitude', 'longtitude'

PAGES_CHANGES_ALLOWED = ('/cities',)
