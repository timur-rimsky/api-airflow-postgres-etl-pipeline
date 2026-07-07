import os
from pathlib import Path
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_DIR / ".env"

load_dotenv(ENV_PATH)


def get_required_env(name):
    value = os.getenv(name)

    if value is None or value.strip() == "":
        raise ValueError(f"Missing required environment variable: {name}")
    
    return value


def get_db_config():
    return {
        "dbname":   get_required_env("POSTGRES_DB"),
        "user":     get_required_env("POSTGRES_USER"),
        "password": get_required_env("POSTGRES_PASSWORD"),
        "host":     get_required_env("POSTGRES_HOST"),
        "port":     int(get_required_env("POSTGRES_PORT"))
    }


def get_api_url():
    return get_required_env("API_URL")


