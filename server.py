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
        body: Optional[bytes] = None,
        code_message: Optional[str] = None,
        headers: Optional[dict] = None,
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
            self.wfile.write(body.encode())

    def do_GET(self) -> None:
        try:
            page = self.page()
        except psycopg.Error:
            code, page = http_codes.SERVER_ERROR, None
            self.db_connection.rollback()
        else:
            code = http_codes.OK
        self.respond(code, page)

    def check_change_allowed(self) -> bool:
        return any(self.path.startswith(page) for page in config.PAGES_CHANGES_ALLOWED)

    def change_allowed(self) -> bool:
        if not self.check_change_allowed():
            self.respond(http_codes.NOT_ALLOWED, headers=config.ALLOW_READ)
            return False
        return True
    
    def check_auth(self) -> bool:
        if config.KEY_HEADER not in self.headers.keys():
            return False
        return db.check_token(self.db_cursor, self.headers.get(config.KEY_HEADER))
    
    def auth(self) -> bool:
        if not self.check_auth():
            self.respond(http_codes.FORBIDDEN)
            return False
        return True

    def auth_and_allow(self) -> bool:
        if not self.change_allowed():
            return False
        if not self.auth():
            return False
        return True

    def read_json_body(self) -> dict | None:        
        content_len = self.headers.get(config.CONTENT_LENGTH)
        if not content_len or not content_len.isdigit():
            msg = f'{config.CONTENT_LENGTH} header is not specified or not int'
            self.respond(http_codes.BAD_REQUEST, msg.encode())
            return
        body = self.rfile.read(int(content_len))
        try:
            return json.loads(body)
        except json.JSONDecodeError as error:
            self.respond(http_codes.BAD_REQUEST, str(error).encode())
            return None

    def do_POST(self) -> None:
        if not self.auth_and_allow():
            return
        content = self.read_json_body()
        if content is None:
            return
        if set(config.CITY_REQUIRED_KEYS) != set(content.keys()):
            msg = f'wrong body json keys, required keys are: {config.CITY_REQUIRED_KEYS}'
            self.respond(http_codes.BAD_REQUEST, msg)
            return
        city_params = [content[attr] for attr in config.CITY_REQUIRED_KEYS]
        try:
            added = db.insert_city(self.db_cursor, self.db_connection, city_params)
        except psycopg.errors.UniqueViolation:
            self.respond(http_codes.BAD_REQUEST, 'already exists')
            self.db_connection.rollback()
            return
        except psycopg.Error as error:
            self.respond(http_codes.SERVER_ERROR, str(error))
            self.db_connection.rollback()
            return
        if added:
            self.respond(http_codes.CREATED) # TODO header content-location
        else:
            self.respond(http_codes.NO_CONTENT)

    def do_DELETE(self) -> None:
        if not self.auth_and_allow():
            return
        city_key = 'name'
        query = get_query(self.path)
        city = query.get(city_key)
        if not city:
            msg = f'city key {city_key} is not provided'
            self.respond(http_codes.BAD_REQUEST, msg)
            return
        try:
            rows = db.delete_city(self.db_cursor, self.db_connection, city)
        except psycopg.Error as error:
            self.respond(http_codes.SERVER_ERROR, str(error))
            self.db_connection.rollback()
            return
        if rows > 1:
            msg = f'all cities with name={city} deleted'
            self.respond(http_codes.OK, msg)
        elif rows == 1:
            self.respond(http_codes.NO_CONTENT)
        else:
            msg = f'matching city with name={city} not found'
            self.respond(http_codes.OK, msg)

    def do_PUT(self) -> None:
        if not self.auth_and_allow():
            return
        city_key = 'name'
        query = get_query(self.path)
        city = query.get(city_key)
        if city is None or not db.check_city(self.db_cursor, city):
            self.do_POST()
            return
        content = self.read_json_body()
        if content is None:
            self.respond(http_codes.BAD_REQUEST, f'PUT must include message body')
            return
        for key in content.keys():
            if key not in config.CITY_REQUIRED_KEYS:
                self.respond(http_codes.BAD_REQUEST, f'key {key} is not specified for instance')
                return
        if db.update_city(self.db_cursor, self.db_connection, content, city):
            self.respond(http_codes.OK, f'instance {city} was updated')
        else:
            self.respond(http_codes.SERVER_ERROR, f'failed to update instance {city}')

    def do_HEAD(self) -> None:
        self.respond(http_codes.OK)


if __name__ == '__main__':
    server = HTTPServer((config.HOST, config.PORT), set_handler_key(RequestHandler))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Interrupted by user!')
    finally:
        server.server_close()
