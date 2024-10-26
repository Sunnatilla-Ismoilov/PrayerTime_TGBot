from aiogram.fsm.state import State, StatesGroup


class CityInputState(StatesGroup):
    waiting_for_city_name = State()
