from http.server import HTTPServer, BaseHTTPRequestHandler
import config 
import http_codes
import views
import os
import dotenv
import weather
import db
from typing import Optional
import psycopg
import json


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
    def weather(self) -> str:
        query = get_query(self.path)
        city_name = query.get('city')
        if city_name:
            coords = db.get_coords(self.db_cursor, views.plusses_to_spaces(city_name))
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

    def respond(self,
        code: int, 
        code_message: Optional[str] = None,
        headers: Optional[dict] = None,
        body: Optional[bytes] = None,
    ) -> None:
        if code_message:
            self.send_response(code, code_message)
        else:
            self.send_response(code)
        self.send_header(*config.CONTENT_HEADER)
        if headers:
            for header_key, header_value in headers.items():
                self.send_header(header_key, header_value)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self) -> None:
        try:
            page = self.page()
        except psycopg.Error:
            code, page = http_codes.SERVER_ERROR, None
            self.db_connection.rollback()
        else:
            code = http_codes.OK
        self.respond(code, body=page.encode() if page else None)

    def change_not_allowed(self) -> None:
        if not self.path.startswith('/cities'):
            self.respond(http_codes.NOT_ALLOWED, headers=config.ALLOW_READ)
            return True
        return False

    def do_POST(self) -> None:
        if self.change_not_allowed():
            return
        content_len = self.headers.get(config.CONTENT_LENGTH)
        if not content_len or not content_len.isdigit():
            msg = f'{config.CONTENT_LENGTH} header is not specified or not int'
            self.respond(http_codes.BAD_REQUEST, body=msg.encode())
            return
        body = self.rfile.read(int(content_len))
        try:
            content = json.loads(body)
        except json.JSONDecodeError as error:
            self.respond(http_codes.BAD_REQUEST, body=str(error).encode())
            return
        if set(config.CITY_REQUIRED_KEYS) != set(content.keys()):
            msg = f'wrong body json keys, required keys are: {config.CITY_REQUIRED_KEYS}'
            self.respond(http_codes.BAD_REQUEST, body=msg.encode())
            return
        city_params = [content[attr] for attr in config.CITY_REQUIRED_KEYS]
        try:
            added = db.insert_city(self.db_cursor, self.db_connection, city_params)
        except psycopg.errors.UniqueViolation:
            self.respond(http_codes.BAD_REQUEST, body='already exists'.encode())
            self.db_connection.rollback()
        except psycopg.Error as error:
            self.respond(http_codes.SERVER_ERROR, body=str(error).encode())
            self.db_connection.rollback()
            return
        if added:
            self.respond(http_codes.CREATED) # TODO header content-location
        else:
            self.respond(http_codes.NO_CONTENT)

    def do_DELETE(self) -> None:
        if self.change_not_allowed():
            return
        city_key = 'name'
        query = get_query(self.path)
        city = query.get(city_key)
        if not city:
            msg = f'city key {city_key} is not provided'
            self.respond(http_codes.BAD_REQUEST, body=msg.encode())
            return
        try:
            rows = db.delete_city(self.db_cursor, self.db_connection, city)
        except psycopg.Error as error:
            self.respond(http_codes.SERVER_ERROR, body=str(error).encode())
            self.db_connection.rollback()
            return
        if rows > 1:
            msg = f'all cities with name={city} deleted'
            self.respond(http_codes.OK, body=msg.encode())
        elif rows == 1:
            self.respond(http_codes.NO_CONTENT)
        else:
            msg = f'matching city with name={city} not found'
            self.respond(http_codes.OK, body=msg.encode())

        
if __name__ == '__main__':
    server = HTTPServer((config.HOST, config.PORT), set_handler_key(RequestHandler))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Interrupted by user!')
    finally:
        server.server_close()
