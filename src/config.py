import os
from pathlib import Path

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from pydantic_settings import BaseSettings

project_root = Path(__file__).resolve().parent.parent
env_file_path = project_root / '.env'


class Settings(BaseSettings):
    BOT_TOKEN: str = "telegram_bot_token"
    MONKEYTYPE_AUTH_TOKEN: str = "AIzaSyB5m_AnO575kvWriahcF1SFIWp8Fj3gQno"
    AUTH_DOMAIN: str = "securetoken.googleapis.com"
    TOKEN_URL: str = "https://securetoken.googleapis.com/v1/token"
    EMAIL: str = "XXXXXXXXXXXXXXXXXXXX"
    PASSWORD: str = "XXXXXXXXXXXXXXXXXXXX"
    TAG_RESULT: str = None
    LOG_MODE: str = "INFO"

    @property
    def DB_PATH(self):
        return project_root / "mtype.db" if not os.getenv('TEST_ENVIRONMENT') else project_root / "mtype_test.db"

    class Config:
        env_file = env_file_path
        env_file_encoding = 'utf-8'



settings = Settings()

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
