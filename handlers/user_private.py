import os
import aiohttp
from aiogram import F
from typing import Any
from responses import *
from keyboards import kbds
from aiogram import types, Router
from aiogram.types import Message
from aiogram.filters import Command
from fsm.states import CityInputState
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv, find_dotenv
from filters.chat_types import ChatTypeFilter

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))
load_dotenv(find_dotenv())


@user_private_router.message(Command('start', ignore_case=True))
async def cmd_start(message: types.Message):
    await message.answer(start_message(message.from_user.full_name),
                         reply_markup=kbds.start_kb)


@user_private_router.message(Command('help', ignore_case=True))
async def cmd_start(message: types.Message):
    await message.answer(start_message(message.from_user.full_name),
                         reply_markup=kbds.start_kb)


@user_private_router.message(Command('about', ignore_case=True))
async def cmd_start(message: types.Message):
    await message.answer((author_info_message()),
                         reply_markup=kbds.start_kb)


@user_private_router.message(F.content_type == types.ContentType.LOCATION)
async def handle_location(message: types.Message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    location_name = await get_city_country(latitude, longitude)
    prayer_times = await get_prayer_times(location_name['city'], location_name['country'])
    await message.answer(f"{location_detected_message(location_name['city'], 
                                                      location_name['country'])} - {prayer_times}")
    await message.answer("Выберите дальнейшие действия:",
                         reply_markup=kbds.confirm_location)


@user_private_router.message(F.text.casefold() == "ввести название города  🗺")
async def without_puree(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, введите название вашего города:")
    await state.set_state(CityInputState.waiting_for_city_name)


@user_private_router.message(CityInputState.waiting_for_city_name, F.text)
async def capture_city_name(message: Message, state: FSMContext):
    city_name = message.text
    location_name = await get_country(city_name)
    prayer_times = await get_prayer_times(location_name['city'], location_name['country'])
    if prayer_times:
        await message.answer(f"Вы ввели: {location_name['city']}, {location_name['country']}\n"
                             f"Теперь я нашел для вас время молитв:\n{prayer_times}")
    else:
        await message.answer("Не удалось получить время молитвы для указанного города.")
    await state.clear()


async def get_city_country(latitude: float, longitude: float) -> Any | None:
    url = f"https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={os.getenv('OPENCAGE_API_KEY')}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data['results']:
                    components = data['results'][0]['components']
                    if 'city' in components and 'country' in components:
                        return {
                            'city': components['city'],
                            'country': components['country']
                        }
                    return components
            return None


async def get_country(city: str) -> Any | None:
    url = f"https://api.opencagedata.com/geocode/v1/json?q={city}&key={os.getenv('OPENCAGE_API_KEY')}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data['results']:
                    components = data['results'][0]['components']
                    print(components)
                    if 'city' in components and 'country' in components:
                        return {
                            'city': components['city'],
                            'country': components['country']
                        }
            return None


async def get_prayer_times(city: str, country: str) -> str | None:
    params = {
        'city': city,
        'country': country,
        'method': 3,
        'school': 1,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(os.getenv('ALADHAN_API_URL'), params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                if 'data' in data:
                    timings = data['data']['timings']
                    formatted_times = (
                        f"Фаджр: {timings['Fajr']}\n"
                        f"Восход солнца: {timings['Sunrise']}\n"
                        f"Зухр: {timings['Dhuhr']}\n"
                        f"Аср: {timings['Asr']}\n"
                        f"Магриб: {timings['Maghrib']}\n"
                        f"Иша: {timings['Isha']}\n"
                    )
                    return formatted_times
            return None
