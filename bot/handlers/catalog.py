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
from bot.i18n import t
from bot.keyboards.main_menu import CATALOG_BUTTONS
from bot.services.catalog import get_product_any, list_categories, list_products

router = Router()


@router.message(Command("catalog"))
@router.message(F.text.in_(CATALOG_BUTTONS))
async def show_categories(message: Message):
    categories = await list_categories()
    if not categories:
        await message.answer(t("catalog_empty"))
        return
    await message.answer(t("choose_category"), reply_markup=categories_keyboard(categories))


@router.callback_query(BackToCategories.filter())
async def back_to_categories(callback: CallbackQuery):
    categories = await list_categories()
    await callback.message.edit_text(t("choose_category"), reply_markup=categories_keyboard(categories))
    await callback.answer()


@router.callback_query(CategoryCallback.filter())
async def show_products(callback: CallbackQuery, callback_data: CategoryCallback):
    products = await list_products(callback_data.id)
    text = t("choose_product") if products else t("category_empty")
    await callback.message.edit_text(text, reply_markup=products_keyboard(products))
    await callback.answer()


@router.callback_query(ProductCallback.filter())
async def show_product(callback: CallbackQuery, callback_data: ProductCallback, state: FSMContext):
    product = await get_product_any(callback_data.id)
    if product is None:
        await callback.answer(t("product_not_found"), show_alert=True)
        return
    parts = [f"<b>{html.escape(product.name)}</b>"]
    if product.description:
        parts.append(html.escape(product.description))
    parts.append(t("product_price", price=f"{product.price:.0f}"))
    if not product.is_available:
        # Недоступный товар показываем, но заказать его нельзя
        parts.append(t("out_of_stock"))
    text = "\n\n".join(parts)
    data = await state.get_data()
    qty = data.get("cart", {}).get(str(product.id), 0)
    await callback.message.edit_text(text, reply_markup=product_keyboard(product, qty))
    await callback.answer()
