from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import localized, t
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
        builder.button(text=localized(category, "name"), callback_data=CategoryCallback(id=category.id))
    builder.adjust(2)
    return builder.as_markup()


def products_keyboard(products: list[Product]):
    builder = InlineKeyboardBuilder()
    for product in products:
        # Цвет кнопки в Telegram не меняется, поэтому недоступный товар помечаем значком и текстом
        if product.is_available:
            text = f"{localized(product, 'name')} — {product.price:.0f} ₸"
        else:
            text = t("product_btn_unavailable", name=localized(product, "name"))
        builder.button(text=text, callback_data=ProductCallback(id=product.id))
    builder.button(text=t("btn_to_categories"), callback_data=BackToCategories())
    builder.adjust(1)
    return builder.as_markup()


def product_keyboard(product: Product, qty: int = 0):
    # Недоступный товар: в корзину добавить нельзя, только вернуться назад
    if not product.is_available:
        builder = InlineKeyboardBuilder()
        builder.button(text=t("btn_back"), callback_data=CategoryCallback(id=product.category_id))
        return builder.as_markup()

    # Выбор количества виден сразу (0 шт); первое нажатие на ➕ кладёт товар в корзину
    builder = InlineKeyboardBuilder()
    builder.button(text="➖", callback_data=CartCallback(action="minus", id=product.id))
    builder.button(text=t("qty_pcs", qty=qty), callback_data=CartCallback(action="noop"))
    builder.button(text="➕", callback_data=CartCallback(action="add", id=product.id))
    builder.button(text=t("btn_open_cart"), callback_data=CartCallback(action="show"))
    builder.adjust(3, 1)
    builder.button(text=t("btn_back"), callback_data=CategoryCallback(id=product.category_id))
    return builder.as_markup()
