import logging

from config import settings


def setup_logger(name: str, level: str = settings.LOG_MODE):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    log_level = getattr(logging, level.upper(), logging.DEBUG)
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(console_handler)

    return logger


main_logger = setup_logger('auth_client')
auth_logger = setup_logger('auth_client')
api_logger = setup_logger('api')
db_logger = setup_logger('database')
bot_logger = setup_logger('bot')
