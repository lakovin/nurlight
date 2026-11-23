from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import t
from delivery.models import Product


class CartCallback(CallbackData, prefix="cart"):
    action: str  # add, minus, show, clear, checkout, noop
    id: int = 0
    where: str = "card"  # card = карточка товара, cart = окно корзины


def cart_keyboard(items: list[tuple[Product, int]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product, qty in items:
        builder.button(text="➖", callback_data=CartCallback(action="minus", id=product.id, where="cart"))
        builder.button(text=f"{product.name} × {qty}", callback_data=CartCallback(action="noop"))
        builder.button(text="➕", callback_data=CartCallback(action="add", id=product.id, where="cart"))
    builder.button(text=t("btn_checkout"), callback_data=CartCallback(action="checkout"))
    builder.button(text=t("btn_clear"), callback_data=CartCallback(action="clear"))
    builder.adjust(*([3] * len(items)), 1)
    return builder.as_markup()