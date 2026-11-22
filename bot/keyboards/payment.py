from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DemoPayCallback(CallbackData, prefix="demopay"):
    order_id: int


def demo_pay_keyboard(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Оплатить (тест)",
        callback_data=DemoPayCallback(order_id=order_id),
    )
    return builder.as_markup()
