import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, FSInputFile
from config import TOKEN, WEATHER_API_KEY
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp
import logging

bot = Bot(TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    name = State()
    age = State()
    city = State()


def init_db():
    conn = sqlite3.connect('user_data.db')
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        city TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

init_db()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer('Привет! Как тебя зовут?')
    await state.set_state(Form.name)

@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Сколько тебе лет?')
    await state.set_state(Form.age)

@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer('В каком городе ты живёшь?')
    await state.set_state(Form.city)

@dp.message(Form.city)
async def city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    user_data = await state.get_data()

    conn = sqlite3.connect('user_data.db')
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO users (name, age, city) VALUES (?, ?, ?)
    ''', (user_data['name'], user_data['age'], user_data['city']))

    conn.commit()
    conn.close()

    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://api.openweathermap.org/data/2.5/weather?q={user_data['city']}&appid={WEATHER_API_KEY}&units=metric") as response:
            if response.status == 200:
                weather_data = await response.json()
                main = weather_data['main']
                weather = weather_data['weather'][0]

                temp = main['temp']
                humidity = main['humidity']
                description = weather['description']

                weather_report = (f"Город - {user_data['city']}\nТемпература - {temp}\nВлажность воздуха - {humidity}\nОписание погоды - {description}")
                await message.answer(weather_report)
            else:
                await message.answer(f"Не удалось получить данные о погоде для {user_data['city']}. Проверьте название города.")

    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())