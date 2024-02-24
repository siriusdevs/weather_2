from http.server import HTTPServer, BaseHTTPRequestHandler
from config import HOST, PORT, CONTENT_HEADER
import http_codes
import views
import os
import dotenv
import weather
import db


def set_handler_key(class_: type) -> type:
    dotenv.load_dotenv()
    connection, cursor = db.connect()
    setattr(class_, 'yandex_key', os.environ.get('YANDEX_KEY'))
    setattr(class_, 'db_connection', connection)
    setattr(class_, 'db_cursor', cursor)
    return class_


def get_query(path: str) -> dict:
    qm_mark = '?'
    qm_index = path.find(qm_mark)
    if qm_index == -1 or qm_index == len(path) - 1:
        return {}
    query = {}
    path = path[qm_index+1:]
    for pair in path.split('&'):
        if '=' not in pair:
            continue
        attr, value = path.split('=')
        if value.isdigit():
            query[attr] = int(value)
            continue
        try:
            number = float(value)
        except ValueError:
            query[attr] = value
        else:
            query[attr] = number
    return query


class RequestHandler(BaseHTTPRequestHandler):
    def weather(self) -> None:
        query = get_query(self.path)
        city_name = query.get('city')
        if city_name:
            coords = db.get_coords(self.db_cursor, city_name)
            if coords:
                lat, lon = coords
                weather_data = weather.get_weather(lat, lon, self.yandex_key)
                return views.weather_page(weather_data)
        cities_names = db.get_cities_names(self.db_cursor)
        return views.weather_dummy_page(cities_names)

    def page(self) -> str:
        if self.path.startswith('/weather'):
            return self.weather()
        elif self.path.startswith('/cities'):
            cities = db.get_cities(self.db_cursor)
            return views.cities_page(cities)
        return views.main_page()

    def do_GET(self):
        self.send_response(http_codes.OK)
        self.send_header(*CONTENT_HEADER)
        self.end_headers()
        self.wfile.write(self.page().encode())

if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), set_handler_key(RequestHandler))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Interrupted by user!')
    finally:
        server.server_close()
