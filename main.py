import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.filters.state import StateFilter
from aiogram import Router

from weather import get_weather
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

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
