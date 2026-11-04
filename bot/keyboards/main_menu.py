from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

CATALOG_BUTTON = "🛍 Каталог"
CART_BUTTON = "🛒 Корзина"

main_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=CATALOG_BUTTON), KeyboardButton(text=CART_BUTTON)]],
    resize_keyboard=True,
)