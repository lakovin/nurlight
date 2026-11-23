from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import t
from bot.keyboards.main_menu import main_menu


class DemoPayCallback(CallbackData, prefix="demopay"):
    order_id: int


def demo_pay_keyboard(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t("btn_pay_demo"),
        callback_data=DemoPayCallback(order_id=order_id),
    )
    return builder.as_markup()


def demo_window_keyboard(url: str) -> ReplyKeyboardMarkup:
    """Главное меню, а над ним кнопка окна оплаты.

    Окно возвращает результат боту только с обычной клавиатуры (не inline):
    тогда странице не нужен свой сервер.
    """
    menu = main_menu()
    pay = KeyboardButton(text=t("btn_pay_window"), web_app=WebAppInfo(url=url))
    return ReplyKeyboardMarkup(
        keyboard=[[pay], *menu.keyboard],
        resize_keyboard=True,
    )
