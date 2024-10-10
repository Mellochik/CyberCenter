import asyncio
import logging
import os

import aiohttp
from aiohttp import ClientError

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

from handlers import help, add, news


bot = Bot(token=os.environ.get('BOT_TOKEN'))

dp = Dispatcher()

dp.include_router(help.router)
dp.include_router(add.router)
dp.include_router(news.router)

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить источник'), KeyboardButton(
            text='Получить новости за последний час')],
        [KeyboardButton(text='Получить новости за последние сутки'),
         KeyboardButton(text='Помощь')]
    ],
    resize_keyboard=True
)


@dp.message(CommandStart())
@dp.message(F.text.lower() == 'начать')
async def command_start_handler(message: Message) -> None:
    """Обработчик команды /start"""

    try:
        payload = {
            "id": message.from_user.id,
            "username": message.from_user.username,
            "full_name": message.from_user.full_name
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(os.environ.get('MONITORING_URL') + "/api/v1/user", json=payload) as response:
                if response.status in (200, 201):
                    response_json = await response.json()
                    await message.answer(response_json['message'] + ' Я новостной БОТ, нажми на "Помощь", чтобы узнать мои команды!!!', reply_markup=keyboard)
                else:
                    await message.answer('Произошла ошибка')
    except ClientError:
        await message.answer("Сервер недоступен, попробуйте позже")


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
