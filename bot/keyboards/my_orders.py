from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.catalog import BackToCategories
from delivery.models import Order


class MyOrdersCallback(CallbackData, prefix="my"):
    # list, view, refresh, cancel, cancel_confirm, cancel_abort
    action: str
    order_id: int = 0


def orders_list_keyboard(orders: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for order in orders:
        builder.button(
            text=f"№{order['number']} — {order['status_text']}",
            callback_data=MyOrdersCallback(
                action="view", order_id=order["id"]
            ),
        )

    builder.button(text="🛍 Каталог", callback_data=BackToCategories())

    builder.adjust(1)
    return builder.as_markup()


def empty_orders_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🛍 Каталог", callback_data=BackToCategories())
    return builder.as_markup()


def retry_list_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔁 Повторить",
        callback_data=MyOrdersCallback(action="list"),
    )
    return builder.as_markup()


def order_card_keyboard(order: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    order_id = order["id"]
    status = order["status"]

    builder.button(
        text="🔄 Обновить",
        callback_data=MyOrdersCallback(action="refresh", order_id=order_id),
    )

    # Отмена доступна только пока заказ «Новый»
    if status == Order.Status.NEW:
        builder.button(
            text="❌ Отменить заказ",
            callback_data=MyOrdersCallback(action="cancel", order_id=order_id),
        )

    if status in (Order.Status.DELIVERED, Order.Status.CANCELLED):
        builder.button(text="🛍 Заказать ещё", callback_data=BackToCategories())

    builder.button(
        text="⬅️ К списку",
        callback_data=MyOrdersCallback(action="list"),
    )

    builder.adjust(1)
    return builder.as_markup()


def cancel_confirm_keyboard(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Да, отменить",
        callback_data=MyOrdersCallback(
            action="cancel_confirm", order_id=order_id
        ),
    )
    builder.button(
        text="⬅️ Нет, оставить",
        callback_data=MyOrdersCallback(
            action="cancel_abort", order_id=order_id
        ),
    )

    builder.adjust(1)
    return builder.as_markup()


def back_to_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ К заказу",
        callback_data=MyOrdersCallback(action="view", order_id=order_id),
    )
    return builder.as_markup()


def after_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🛍 Каталог", callback_data=BackToCategories())
    builder.adjust(1)
    return builder.as_markup()
