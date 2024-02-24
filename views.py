from config import MAIN_TEMPLATE, WEATHER_TEMPLATE

def main_page() -> str:
    with open(MAIN_TEMPLATE, 'r') as file:
        return file.read()


def weather_page(weather_params: dict) -> str:
    with open(WEATHER_TEMPLATE, 'r') as file:
        return file.read().format(**weather_params)