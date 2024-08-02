import random
import string
from datetime import datetime, timezone


def generate_auth_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def format_duration(seconds):
    if seconds >= 3600:
        return f"{seconds / 3600:.2f} ч."
    elif seconds >= 60:
        return f"{seconds / 60:.2f} мин."
    else:
        return f"{seconds:.2f} сек."


def time_since(timestamp):
    if isinstance(timestamp, int):
        timestamp = timestamp / 1000

    test_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    test_time_local = test_time.astimezone()
    now = datetime.now(tz=timezone.utc).astimezone()
    delta = now - test_time_local

    if delta.total_seconds() >= 3600:
        return f"{delta.total_seconds() / 3600:.2f} ч. назад"
    elif delta.total_seconds() >= 60:
        return f"{delta.total_seconds() / 60:.2f} мин. назад"
    else:
        return f"{delta.total_seconds():.2f} сек. назад"


async def get_headers(token):
    HEADERS = {
        'accept': 'application/json',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': f'Bearer {token}',
        'origin': 'https://monkeytype.com',
        'priority': 'u=1, i',
        'referer': 'https://monkeytype.com/',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'x-client-version': '2024.07.28_16.35.cdb926e12'
    }
    return HEADERS
