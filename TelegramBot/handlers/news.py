from aiogram import Router, F, html
from aiogram.filters import Command
from aiogram.types import Message

import aiohttp
from aiohttp import ClientError

import os


router = Router()


@router.message(Command(commands=['news_hour']))
@router.message(F.text.lower() == "получить новости за последний час")
async def command_show_hour(message: Message) -> None:
    """Обработчик команды /show_hour."""

    try:
        payload = {
            "id": message.from_user.id
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(os.environ.get('MONITORING_URL') + "/api/v1/news/hour", json=payload) as response:
                if response.status == 200:
                    response_json = await response.json()

                    if response_json:
                        for item in response_json:
                            await message.answer(
                                text=f'{html.bold("Источник: ")}{item["source"]["title"]}\n'+
                                    f'{html.bold("Описание: ")}{item["source"]["description"]}\n'+
                                    f'{html.bold("Название новости: ")}{item["title"]}\n'+
                                    f'{html.bold("Дата публикации: ")}{item["pub_date"].replace("T", " ")}\n' +
                                    f'{html.blockquote(item["description"])}',
                                parse_mode='HTML'
                            )
                    else:
                        await message.answer(text="Нет новостей за последний час!")
                else:
                    await message.answer(text=f'Не получилось получить новости или у вас их нет!')
    except ClientError:
        await message.answer("Сервер недоступен, попробуйте позже")


@router.message(Command(commands=['news_day']))
@router.message(F.text.lower() == "получить новости за последние сутки")
async def command_show_day(message: Message) -> None:
    """Обработчик команды /show_day."""
    
    try:
        payload = {
            "id": message.from_user.id
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(os.environ.get('MONITORING_URL') + "/api/v1/news/day", json=payload) as response:
                if response.status == 200:
                    response_json = await response.json()
        
                    if response_json:
                        for item in response_json:
                            await message.answer(
                                text=f'{html.bold("Источник: ")}{item["source"]["title"]}\n'+
                                    f'{html.bold("Описание: ")}{item["source"]["description"]}\n'+
                                    f'{html.bold("Название новости: ")}{item["title"]}\n'+
                                    f'{html.bold("Дата публикации: ")}{item["pub_date"].replace("T", " ")}\n' +
                                    f'{html.blockquote(item["description"])}',
                                parse_mode='HTML'
                            )
                    else:
                        await message.answer(text="Нет новостей за последние сутки!")
                else:
                    await message.answer(text=f'Не получилось получить новости или у вас их нет!')
    except ClientError:
        await message.answer("Сервер недоступен, попробуйте позже")
