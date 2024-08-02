import traceback

import aiohttp
import json

from auth_client import AuthClient

from database.db import result_exists, insert_or_replace_result
from logger import api_logger as logger
from tgbot.notify import process_new_record
from utils import get_headers

auth_client = AuthClient()


async def fetch_and_save():
    token = await auth_client.get_auth_token()
    headers = await get_headers(token)
    url = "https://api.monkeytype.com/results"
    async with aiohttp.ClientSession() as session:
        data = await fetch_data(session, url, headers)
        await save_to_db(data)


async def fetch_data(session, url, headers):
    try:
        proxy = None
        async with session.get(url, headers=headers, proxy=proxy) as response:
            if response.status == 200:
                text = await response.text()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    logger.error("Failed to decode JSON data: %s", text)
                    data = {}
            else:
                logger.error(f"Request failed with status: {response.status}")
                logger.error(await response.text())
                data = {}
    except aiohttp.ClientError as e:
        logger.error(f"Client error occurred: {e}")
        data = {}
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        data = {}

    logger.debug("Fetched data: %s", data)
    logger.info(f"Fetched data: {str(data)[:40]}...")
    return data


async def save_to_db(data):
    try:
        if isinstance(data, dict) and 'data' in data:
            data = data['data']

        if not isinstance(data, list):
            logger.warning("Data is not in expected format (list of dicts).")
            return

        if data and all('timestamp' in item for item in data):
            data.sort(key=lambda x: x.get('timestamp', 0))

        for item in data:
            if isinstance(item, dict):
                logger.debug("Processing item: %s", item)
                await process_item(item)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        logger.error(traceback.format_exc())


async def process_item(item):
    if await result_exists(item.get('_id', '')):
        logger.info("Record with id %s already exists. Skipping processing.", item.get('_id', ''))
        return

    await insert_or_replace_result(item)
    await process_new_record(item)
