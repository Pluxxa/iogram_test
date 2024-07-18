import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.filters.state import StateFilter
from aiogram import Router
import random
from gtts import gTTS
import os

from weather import get_weather, translate_to_english
from config import TOKEN

API_TOKEN = TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

class WeatherStates(StatesGroup):
    waiting_for_city = State()

@router.message(Command(commands=["start"]))
async def send_welcome(message: Message):
    await message.answer("Привет! Я бот, который может сообщать о погоде.\nИспользуйте команду /weather, чтобы узнать погоду.")

@router.message(Command(commands=["help"]))
async def send_help(message: Message):
    await message.answer("Список доступных команд:\n/start - Начало работы\n/help - Помощь\n/weather - Узнать погоду")

@dp.message(F.photo)
async def react_photo(message: Message):
    list = ['Ого, какая фотка!', 'Непонятно, что это такое', 'Не отправляй мне такое больше']
    rand_answ = random.choice(list)
    await message.answer(rand_answ)
    await bot.download(message.photo[-1],destination=f'images/{message.photo[-1].file_id}.jpg')


@dp.message(Command('voice'))
async def voice(message: Message):
    training_list = [
        "Тренировка 1:\n1. Скручивания: 3 подхода по 15 повторений\n2. Велосипед: 3 подхода по 20 повторений (каждая сторона)\n3. Планка: 3 подхода по 30 секунд",
        "Тренировка 2:\n1. Подъемы ног: 3 подхода по 15 повторений\n2. Русский твист: 3 подхода по 20 повторений (каждая сторона)\n3. Планка с поднятой ногой: 3 подхода по 20 секунд (каждая нога)",
        "Тренировка 3:\n1. Скручивания с поднятыми ногами: 3 подхода по 15 повторений\n2. Горизонтальные ножницы: 3 подхода по 20 повторений\n3. Боковая планка: 3 подхода по 20 секунд (каждая сторона)"
    ]
    rand_tr = random.choice(training_list)
    tts = gTTS(text=rand_tr, lang='ru')
    tts.save("training.ogg")
    audio = FSInputFile("training.ogg")
    await message.answer_voice(audio)
    os.remove("training.ogg")

@dp.message(Command('training'))
async def training(message: Message):
    training_list = [
       "Тренировка 1:\n1. Скручивания: 3 подхода по 15 повторений\n2. Велосипед: 3 подхода по 20 повторений (каждая сторона)\n3. Планка: 3 подхода по 30 секунд",
       "Тренировка 2:\n1. Подъемы ног: 3 подхода по 15 повторений\n2. Русский твист: 3 подхода по 20 повторений (каждая сторона)\n3. Планка с поднятой ногой: 3 подхода по 20 секунд (каждая нога)",
       "Тренировка 3:\n1. Скручивания с поднятыми ногами: 3 подхода по 15 повторений\n2. Горизонтальные ножницы: 3 подхода по 20 повторений\n3. Боковая планка: 3 подхода по 20 секунд (каждая сторона)"
    ]
    rand_tr = random.choice(training_list)
    await message.answer(f"Это ваша мини-тренировка на сегодня {rand_tr}")
    tts = gTTS(text=rand_tr, lang='ru')
    tts.save("training.mp3")
    audio = FSInputFile('training.mp3')
    await bot.send_audio(message.chat.id, audio)
    os.remove("training.mp3")

@router.message(Command(commands=["weather"]))
async def weather(message: Message, state: FSMContext):
    await message.answer("Введите название города:")
    await state.set_state(WeatherStates.waiting_for_city)

@router.message(StateFilter(WeatherStates.waiting_for_city))
async def process_weather(message: Message, state: FSMContext):
    city = message.text
    weather_info = get_weather(city)
    await message.answer(weather_info)
    await state.clear()

@router.message()
async def translate_message(message: Message):
    # Игнорируем команды
    if message.text.startswith('/'):
        return
    translation = translate_to_english(message.text)
    await message.answer(f"Перевод: {translation}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
