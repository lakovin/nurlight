from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

CATALOG_BUTTON = "🛍 Каталог"
CART_BUTTON = "🛒 Корзина"
MY_ORDERS_BUTTON = "📦 Мои заказы"
AI_BUTTON = "🤖 AI-помощник"
FAQ_BUTTON = "❓ Частые вопросы"

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=CATALOG_BUTTON),
            KeyboardButton(text=CART_BUTTON),
        ],
        [
            KeyboardButton(text=MY_ORDERS_BUTTON),
            KeyboardButton(text=FAQ_BUTTON),
        ],
        [
            KeyboardButton(text=AI_BUTTON),
        ],
    ],
    resize_keyboard=True,
)