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
