
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.main_menu import MY_ORDERS_BUTTON
from bot.services.my_orders import (
    get_client_orders,
    get_client_order,
)
from bot.services.validation import format_money


router = Router()


class MyOrderCallback(CallbackData, prefix="myorder"):
    action: str
    order_id: int = 0



def orders_keyboard(orders: list[dict]):
    """Создаёт кнопки проверки статусов заказов."""
    builder = InlineKeyboardBuilder()

    for order in orders:
        builder.button(
            text=f"🔄 Проверить статус №{order['number']}",
            callback_data=MyOrderCallback(
                action="refresh",
                order_id=order["id"],
            ),
        )

    builder.adjust(1)
    return builder.as_markup()



def format_orders(orders: list[dict]) -> str:
    """Формирует текст истории заказов."""
    lines = ["📦 <b>Мои заказы</b>"]

    for order in orders:
        lines.extend([
            "",
            f"🧾 <b>Заказ №{order['number']}</b>",
            f"📅 {order['date']}",
            f"💰 {format_money(order['total'])}",
            f"📍 Статус: {order['status']}",
        ])

    return "\n".join(lines)


@router.message(Command("orders"))
@router.message(F.text == MY_ORDERS_BUTTON)
async def show_orders(message: Message):
    """Показывает последние пять заказов пользователя."""

    orders = await get_client_orders(message.from_user.id)

    if not orders:
        await message.answer(
            "📦 У вас пока нет заказов.\n\n"
            "Откройте каталог, чтобы оформить первый заказ."
        )
        return

    await message.answer(
        format_orders(orders),
        reply_markup=orders_keyboard(orders),
    )


@router.callback_query(
    MyOrderCallback.filter(F.action == "refresh")
)
async def refresh_order(
    callback: CallbackQuery,
    callback_data: MyOrderCallback,
):
    """Получает актуальный статус одного заказа."""

    order = await get_client_order(
        callback.from_user.id,
        callback_data.order_id,
    )

    if order is None:
        await callback.answer(
            "Заказ не найден.",
            show_alert=True,
        )
        return

    await callback.answer(
        f"Заказ №{order['number']}\n"
        f"Статус: {order['status']}",
        show_alert=True,
    )
