from aiogram import Dispatcher

from config import bot
from logger import bot_logger as logger
from tgbot.handlers import router

async def start_bot():
    logger.info("Starting bot...")

    dp = Dispatcher()
    dp.include_routers(router)
    await dp.start_polling(bot)
