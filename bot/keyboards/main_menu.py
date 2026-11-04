from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

CATALOG_BUTTON = "🛍 Каталог"

main_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=CATALOG_BUTTON)]],
    resize_keyboard=True,
)
