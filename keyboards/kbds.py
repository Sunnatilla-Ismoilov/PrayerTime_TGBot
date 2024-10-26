from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить локацию 📍",
                        request_location=True)],
        [KeyboardButton(text="Ввести название города  🗺")]],
    resize_keyboard=True,
    input_field_placeholder="Выберите метод определения локации",
    one_time_keyboard=True
)

confirm_location = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Правильно ✅")],
        [KeyboardButton(text="Ввести название города  🗺")]
    ],
    resize_keyboard=True
)
