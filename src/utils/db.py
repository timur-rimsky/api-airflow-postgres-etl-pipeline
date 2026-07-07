import psycopg2
from src.utils.settings import get_db_config


def get_connection():
    db_config = get_db_config()

    return psycopg2.connect(**db_config)

