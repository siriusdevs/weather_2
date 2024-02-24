from http.server import HTTPServer, BaseHTTPRequestHandler
from config import HOST, PORT, CONTENT_HEADER
import http_codes
import views
import os
import dotenv
import weather

def set_handler_key(class_: type) -> type:
    setattr(class_, 'yandex_key', os.environ.get('YANDEX_KEY'))
    return class_

class RequestHandler(BaseHTTPRequestHandler):
    def page(self) -> str:
        if self.path.startswith('/weather'):
            return views.weather_page(weather.get_weather(1.0, 1.0, self.yandex_key))
        elif self.path.startswith('/cities'):
            return '' # TODO cities
        return views.main_page()

    def do_GET(self):
        self.send_response(http_codes.OK)
        self.send_header(*CONTENT_HEADER)
        self.end_headers()
        self.wfile.write(self.page().encode())

if __name__ == '__main__':
    dotenv.load_dotenv()
    server = HTTPServer((HOST, PORT), set_handler_key(RequestHandler))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Interrupted by user!')
    finally:
        server.server_close()
