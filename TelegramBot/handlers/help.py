from aiogram import Router, F, html
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command(commands=['help']))
@router.message(F.text.lower() == "помощь")
async def command_start_handler(message: Message) -> None:
    """Обработчик команды /help."""
    
    await message.answer(f'{html.bold("Бот создан для просмотра новостей из ваших источников")}\n\n' +
                         'Мои команды:\n' +
                         '/add - добавление источника новостей\n' +
                         '/news_hour - получение всех новостей со всех источников за последний час\n' +
                         '/news_day - получение всех новостей со всех источников за последние сутки\n' +
                         '/help - помощь', parse_mode='HTML')
