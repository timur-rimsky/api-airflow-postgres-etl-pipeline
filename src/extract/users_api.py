import requests
from src.utils.settings import get_api_url


def fetch_users():
    api_url = get_api_url()

    response = requests.get(api_url, timeout=10)
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise ValueError("Invalid API response: expected a list of users")

    return data
