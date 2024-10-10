from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from pydantic import BaseModel, HttpUrl, ValidationError

import aiohttp
from aiohttp import ClientError

import os



class SourceUrl(BaseModel):
    """Класс для валидации URL-адреса источника."""
    
    url: HttpUrl


router = Router()


class AddUrl(StatesGroup):
    """Класс группы состояний для обработки события добавления URL-адреса."""
    
    writing_url = State()


@router.message(Command('add'))
@router.message(F.text.lower() == 'добавить источник')
async def command_add_url(message: Message, state: FSMContext) -> None:
    """Обработчик команды /add."""
    
    await message.answer(text='Введите URL-адресс источника:')
    await state.set_state(AddUrl.writing_url)


@router.message(AddUrl.writing_url)
async def command_parse_url(message: Message, state: FSMContext) -> None:
    """Проверка URL-адреса на правильность."""
    
    try:
        url = SourceUrl(url=message.text)

        payload = {
            "user": {
                "id": message.from_user.id
            },
            "url": {
                "url": message.text
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(os.environ.get('MONITORING_URL') + "/api/v1/add", json=payload) as response:
                response_json = await response.json()
                
                await message.answer(text=response_json['message'] + f'{message.text}')
    except ValidationError:
        await message.answer(text='Некорректный URL')
    except ClientError:
        await message.answer("Сервер недоступен, попробуйте позже")
    finally:
        await state.clear()
