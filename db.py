import psycopg
import os
import config
import db_query


def connect() -> tuple[psycopg.Connection, psycopg.Cursor]:
    try:
        port = int(os.environ.get('PG_PORT', default=config.DEFAULT_PG_PORT))
    except ValueError:
        port = config.DEFAULT_PG_PORT
    
    credentials = {
        'host': os.environ.get('PG_HOST', default=config.HOST),
        'port': port,
        'user': os.environ.get('PG_USER'),
        'password': os.environ.get('PG_PASSWORD'),
        'dbname': os.environ.get('PG_DBNAME'),
    }
    connection = psycopg.connect(**credentials)
    return connection, connection.cursor()


def get_cities(cursor: psycopg.Cursor) -> list[tuple]:
    cursor.execute(db_query.GET_CITIES)
    return cursor.fetchall()


def get_cities_names(cursor: psycopg.Cursor) -> list[str]:
    return [city for city, _, _ in get_cities(cursor)]


def get_coords(cursor: psycopg.Cursor, city_name: str) -> tuple[float, float]:
    cursor.execute(db_query.GET_COORDS, params=(city_name,))
    return cursor.fetchone()


def insert_city(
    cursor: psycopg.Cursor, 
    connection: psycopg.Connection,
    city_params: tuple,
) -> bool:
    cursor.execute(db_query.INSERT_CITY, params=city_params)
    connection.commit()
    return bool(cursor.rowcount)


def delete_city(
    cursor: psycopg.Cursor, 
    connection: psycopg.Connection,
    city_name: str,
) -> int:
    cursor.execute(db_query.DELETE_CITY, params=(city_name,))
    connection.commit()
    return cursor.rowcount
