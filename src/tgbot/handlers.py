

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from database.db import store_authorization, is_authorized, store_auth_code, check_auth_code
from utils import generate_auth_code

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if await is_authorized(user_id):
        await message.reply("Вы уже авторизованы! Добро пожаловать.")
    else:
        await message.reply("Вы не авторизованы. Введите команду /auth, чтобы начать процесс авторизации.")

@router.message(Command("auth"))
async def cmd_auth(message: Message):
    user_id = message.from_user.id
    auth_code = generate_auth_code()
    await store_auth_code(user_id, auth_code)
    print(f"Код авторизации для пользователя {user_id}: {auth_code}")
    await message.reply("Код авторизации был сгенерирован. Проверьте консоль и введите код с помощью команды /verify код.")

@router.message(Command("verify"))
async def cmd_verify(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) != 2:
        await message.reply("Пожалуйста, используйте команду /verify код.")
        return

    auth_code = args[1]
    if await check_auth_code(user_id, auth_code):
        await message.reply("Авторизация успешна.")
        await store_authorization(user_id)
    else:
        await message.reply("Неверный код авторизации или он истек.")