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

class RequestHandler(BaseHTTPRequestHandler):
    def page(self) -> str:
        if self.path.startswith('/weather'):
            return views.weather_page(weather.get_weather(1.0, 1.0, self.yandex_key))
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
