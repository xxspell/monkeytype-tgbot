import asyncio

from external_api import fetch_and_save
from database.db import init_db
from tgbot.bot import start_bot
from logger import main_logger as logger






async def periodic_task(interval):
    while True:
        await fetch_and_save()
        logger.info(f"Next data parsing in {interval} seconds")
        await asyncio.sleep(interval)


async def main():
    try:
        await init_db()
        periodic = asyncio.create_task(periodic_task(3600))
        bot = asyncio.create_task(start_bot())

        await asyncio.gather(periodic, bot)
    except KeyboardInterrupt:

        print("Exiting...")
        exit()

if __name__ == "__main__":
    asyncio.run(main())
