from contextlib import contextmanager

import psycopg2

from src.utils.settings import get_db_config


def get_connection():
    db_config = get_db_config()

    return psycopg2.connect(**db_config)


@contextmanager
def get_db_cursor():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        yield connection, cursor

        connection.commit()

    except Exception:
        if connection is not None:
            connection.rollback()

        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()
