from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import t


class DemoPayCallback(CallbackData, prefix="demopay"):
    order_id: int


def demo_pay_keyboard(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t("btn_pay_demo"),
        callback_data=DemoPayCallback(order_id=order_id),
    )
    return builder.as_markup()
