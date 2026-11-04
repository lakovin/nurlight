import html

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.cart import CartCallback, cart_keyboard
from bot.keyboards.catalog import product_keyboard
from bot.keyboards.main_menu import CART_BUTTON
from bot.services.cart import get_cart_items
from bot.services.catalog import get_product

router = Router()

EMPTY_TEXT = "Корзина пуста. Загляните в каталог 🛍"


def cart_text(items) -> str:
    lines = ["🛒 <b>Ваша корзина</b>\n"]
    total = 0
    for product, qty in items:
        subtotal = product.price * qty
        total += subtotal
        lines.append(f"{html.escape(product.name)}: {qty} × {product.price:.0f} = {subtotal:.0f} ₸")
    lines.append(f"\n<b>Итого: {total:.0f} ₸</b>")
    return "\n".join(lines)


@router.message(Command("cart"))
@router.message(F.text == CART_BUTTON)
async def show_cart(message: Message, state: FSMContext):
    data = await state.get_data()
    items = await get_cart_items(data.get("cart", {}))
    if not items:
        await message.answer(EMPTY_TEXT)
        return
    await message.answer(cart_text(items), reply_markup=cart_keyboard(items))


@router.callback_query(CartCallback.filter(F.action == "show"))
async def show_cart_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items = await get_cart_items(data.get("cart", {}))
    if not items:
        await callback.answer("Корзина пуста", show_alert=True)
        return
    await callback.message.answer(cart_text(items), reply_markup=cart_keyboard(items))
    await callback.answer()


@router.callback_query(CartCallback.filter(F.action.in_({"add", "minus"})))
async def change_quantity(callback: CallbackQuery, callback_data: CartCallback, state: FSMContext):
    data = await state.get_data()
    cart = dict(data.get("cart", {}))
    key = str(callback_data.id)
    qty = cart.get(key, 0)

    if callback_data.action == "add":
        product = await get_product(callback_data.id)
        if product is None:
            await callback.answer("Товар больше недоступен", show_alert=True)
            return
        qty += 1
    else:
        if qty == 0:
            await callback.answer()
            return
        qty -= 1

    if qty > 0:
        cart[key] = qty
    else:
        cart.pop(key, None)
    await state.update_data(cart=cart)

    if callback_data.where == "cart":
        items = await get_cart_items(cart)
        if not items:
            await callback.message.edit_text(EMPTY_TEXT)
        else:
            await callback.message.edit_text(cart_text(items), reply_markup=cart_keyboard(items))
    else:
        product = await get_product(callback_data.id)
        if product is not None:
            await callback.message.edit_reply_markup(reply_markup=product_keyboard(product, qty))
    await callback.answer()


@router.callback_query(CartCallback.filter(F.action == "clear"))
async def clear_cart(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cart={})
    await callback.message.edit_text("Корзина очищена 🗑")
    await callback.answer()


@router.callback_query(CartCallback.filter(F.action == "checkout"))
async def checkout(callback: CallbackQuery):
    # Здесь на следующем шаге начнётся оформление заказа (адрес, телефон, подтверждение)
    await callback.answer("Оформление заказа добавим на следующем шаге", show_alert=True)


@router.callback_query(CartCallback.filter(F.action == "noop"))
async def noop(callback: CallbackQuery):
    await callback.answer()