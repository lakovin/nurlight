from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from delivery.models import Category, Product
from bot.keyboards.cart import CartCallback


class CategoryCallback(CallbackData, prefix="cat"):
    id: int


class ProductCallback(CallbackData, prefix="prod"):
    id: int


class BackToCategories(CallbackData, prefix="cats"):
    pass


def categories_keyboard(categories: list[Category]):
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category.name, callback_data=CategoryCallback(id=category.id))
    builder.adjust(2)
    return builder.as_markup()


def products_keyboard(products: list[Product]):
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(text=f"{product.name} — {product.price:.0f} ₸", callback_data=ProductCallback(id=product.id))
    builder.button(text="⬅️ К категориям", callback_data=BackToCategories())
    builder.adjust(1)
    return builder.as_markup()


def product_keyboard(product: Product, qty: int = 0):
    builder = InlineKeyboardBuilder()
    if qty == 0:
        builder.button(text="➕ В корзину", callback_data=CartCallback(action="add", id=product.id))
        builder.adjust(1)
    else:
        builder.button(text="➖", callback_data=CartCallback(action="minus", id=product.id))
        builder.button(text=f"{qty} шт", callback_data=CartCallback(action="noop"))
        builder.button(text="➕", callback_data=CartCallback(action="add", id=product.id))
        builder.button(text="🛒 Открыть корзину", callback_data=CartCallback(action="show"))
        builder.adjust(3, 1)
    builder.button(text="⬅️ Назад", callback_data=CategoryCallback(id=product.category_id))
    return builder.as_markup()
