import html

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards.catalog import (
    BackToCategories,
    CategoryCallback,
    ProductCallback,
    categories_keyboard,
    product_keyboard,
    products_keyboard,
)
from bot.keyboards.main_menu import CATALOG_BUTTON
from bot.services.catalog import get_product, list_categories, list_products

router = Router()


@router.message(Command("catalog"))
@router.message(F.text == CATALOG_BUTTON)
async def show_categories(message: Message):
    categories = await list_categories()
    if not categories:
        await message.answer("Каталог пока пуст. Загляните позже!")
        return
    await message.answer("Выберите категорию:", reply_markup=categories_keyboard(categories))


@router.callback_query(BackToCategories.filter())
async def back_to_categories(callback: CallbackQuery):
    categories = await list_categories()
    await callback.message.edit_text("Выберите категорию:", reply_markup=categories_keyboard(categories))
    await callback.answer()


@router.callback_query(CategoryCallback.filter())
async def show_products(callback: CallbackQuery, callback_data: CategoryCallback):
    products = await list_products(callback_data.id)
    text = "Выберите товар:" if products else "В этой категории сейчас нет товаров."
    await callback.message.edit_text(text, reply_markup=products_keyboard(products))
    await callback.answer()


@router.callback_query(ProductCallback.filter())
async def show_product(callback: CallbackQuery, callback_data: ProductCallback, state: FSMContext):
    product = await get_product(callback_data.id)
    if product is None:
        await callback.answer("Товар больше недоступен", show_alert=True)
        return
    parts = [f"<b>{html.escape(product.name)}</b>"]
    if product.description:
        parts.append(html.escape(product.description))
    parts.append(f"Цена: {product.price:.0f} ₸")
    text = "\n\n".join(parts)
    data = await state.get_data()
    qty = data.get("cart", {}).get(str(product.id), 0)
    await callback.message.edit_text(text, reply_markup=product_keyboard(product, qty))
    await callback.answer()
