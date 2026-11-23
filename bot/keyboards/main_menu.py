from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from bot.i18n import t, variants

# Кнопки меню на всех языках: по ним срабатывают обработчики,
# какой бы язык ни выбрал клиент (и для старых кнопок в чате)
CATALOG_BUTTONS = variants("btn_catalog")
CART_BUTTONS = variants("btn_cart")
MY_ORDERS_BUTTONS = variants("btn_orders")
FAQ_BUTTONS = variants("btn_faq")
AI_BUTTONS = variants("btn_ai")  # включает старое «🤖 AI-помощник»
LANGUAGE_BUTTONS = variants("btn_lang")

# Все кнопки главного меню: нажатие во время оформления прерывает его
ALL_MENU_BUTTONS = (
    CATALOG_BUTTONS
    | CART_BUTTONS
    | MY_ORDERS_BUTTONS
    | FAQ_BUTTONS
    | AI_BUTTONS
    | LANGUAGE_BUTTONS
)


def main_menu(lang: str | None = None) -> ReplyKeyboardMarkup:
    """Главное меню на языке клиента (по умолчанию — язык текущего обновления)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("btn_catalog", lang)),
                KeyboardButton(text=t("btn_cart", lang)),
            ],
            [
                KeyboardButton(text=t("btn_orders", lang)),
                KeyboardButton(text=t("btn_faq", lang)),
            ],
            [
                KeyboardButton(text=t("btn_ai", lang)),
                KeyboardButton(text=t("btn_lang", lang)),
            ],
        ],
        resize_keyboard=True,
    )
