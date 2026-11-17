from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

CATALOG_BUTTON = "🛍 Каталог"
CART_BUTTON = "🛒 Корзина"
MY_ORDERS_BUTTON = "📦 Мои заказы"

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=CATALOG_BUTTON),
            KeyboardButton(text=CART_BUTTON),
        ],
        [
            KeyboardButton(text=MY_ORDERS_BUTTON),
        ],
    ],
    resize_keyboard=True,
)
