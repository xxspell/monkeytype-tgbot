import json


from config import bot, settings
from database.db import get_authorized_users, get_overall_results, get_predlast_result
from logger import bot_logger as logger
from utils import time_since, format_duration


async def format_test_results(record):
    rows = await get_predlast_result(record)

    if len(rows) > 1:
        previous_record = rows[1]
    else:
        previous_record = None

    current_wpm = record.get('wpm', 0.0)
    current_acc = record.get('acc', 0.0)
    current_test_duration = record.get('testDuration', 0.0)

    timestamp = record.get('timestamp', '')
    comparison = ''
    if previous_record:
        prev_wpm = previous_record.get('wpm', 0.0)
        prev_acc = previous_record.get('acc', 0.0)

        wpm_change = current_wpm - prev_wpm
        acc_change = current_acc - prev_acc

    else:
        comparison = "**Это первый тест с указанным тегом.**"
    wpm_change_str = f"({wpm_change:+.2f})" if previous_record else ''
    acc_change_str = f"({acc_change:+.2f})" if previous_record else ''
    results_message = (
        f"**Вижу тест, пройден {time_since(timestamp)}:**\n"
        f"**WPM:** {current_wpm} {wpm_change_str}\n"
        f"**Аккуратность:** {current_acc}% {acc_change_str}\n"
        f"**Продолжительность теста:** {format_duration(current_test_duration)}\n"
        f"**Теги:** {json.dumps(record.get('tags', []))}\n\n"
        f"{comparison}"
    )

    return results_message


async def get_overall_stats():
    row = await get_overall_results()

    if row:
        avg_wpm, avg_acc, total_duration, test_count = row
        overall_stats = (
            f"**Общая статистика по тестам с указанным тегом:**\n"
            f"**Средний WPM:** {avg_wpm:.2f}\n"
            f"**Средняя аккуратность:** {avg_acc:.2f}%\n"
            f"**Общая продолжительность теста:** {format_duration(total_duration)}\n"
            f"**Количество тестов:** {test_count}"
        )
    else:
        overall_stats = "**Нет данных для статистики.**"

    return overall_stats



async def prepare_message(record):
    test_results = await format_test_results(record)
    overall_stats = await get_overall_stats()

    message = (
        f"{test_results}\n"
        f"**Общая информация:**\n\n"
        f"{overall_stats}"
    )

    return message


async def send_messages(bot, message: str):
    authorized_users = await get_authorized_users()

    for user_id in authorized_users:
        try:
            await bot.send_message(user_id, message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Failed to send message to user {user_id}: {e}")


async def process_new_record(record):
    required_tag = settings.TAG_RESULT

    tags = record.get('tags', [])
    if required_tag in tags:
        logger.info(f"Record contains required tag: {record}")
    else:
        logger.info(f"Record does not contain required tag: {record}")

    logger.info(f"Processing record: {record}")
    message = await prepare_message(record)
    await send_messages(bot, message)