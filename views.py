from config import MAIN_TEMPLATE, WEATHER_TEMPLATE, CITIES_TEMPLATES, WEATHER_DUMMY_TEMPLATE
from typing import Optional


def _load(template_path: str, page_params: Optional[dict] = None) -> str:
    with open(template_path, 'r') as file:
        page = file.read()
    return page.format(**page_params) if page_params else page


def main_page() -> str:
    return _load(MAIN_TEMPLATE)


def weather_page(weather_params: dict) -> str:
    return _load(WEATHER_TEMPLATE, weather_params)
    

def cities_page(cities: list[tuple]) -> str:
    cities_html = html_from_cities(cities)
    return _load(CITIES_TEMPLATES, {'cities': cities_html})


def html_from_cities(cities: list[tuple]) -> str:
    start = '<li> <a href="/weather?city='
    return '\n'.join(f'{start}{city}">{city}</a>, lat:{lat}, lon:{lon}</li>' for city, lat, lon in cities)


def weather_dummy_page(cities_names: list[str]) -> str:
    return _load(WEATHER_DUMMY_TEMPLATE, {'options': form_options(cities_names)})


def form_options(values: list[str]) -> str:
    return '\n'.join(f'<option value="{value}"> {value} </option>' for value in values)


def plusses_to_spaces(text: str) -> str:
    return text.replace('+', ' ')


def spaces_to_plusses(text: str) -> str: # NOTE useless
    return text.replace(' ', '+')
