from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import t
from bot.keyboards.catalog import BackToCategories
from bot.services.payment import can_invoice
from delivery.models import Order


class MyOrdersCallback(CallbackData, prefix="my"):
    # list, view, refresh, cancel, cancel_confirm, cancel_abort,
    # pay (счёт на весь заказ: блюда + доставка)
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

    builder.button(text=t("btn_catalog"), callback_data=BackToCategories())

    builder.adjust(1)
    return builder.as_markup()


def empty_orders_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn_catalog"), callback_data=BackToCategories())
    return builder.as_markup()


def retry_list_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t("btn_retry"),
        callback_data=MyOrdersCallback(action="list"),
    )
    return builder.as_markup()


def order_card_keyboard(order: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    order_id = order["id"]
    status = order["status"]

    builder.button(
        text=t("btn_refresh"),
        callback_data=MyOrdersCallback(action="refresh", order_id=order_id),
    )

    # Оплата одним счётом: блюда + доставка
    if (
        status != Order.Status.CANCELLED
        and not order["paid"]
        and can_invoice(order["total"])
    ):
        builder.button(
            text=t("btn_pay_order"),
            callback_data=MyOrdersCallback(action="pay", order_id=order_id),
        )

    # Отмена доступна только пока заказ «Новый» и не оплачен
    if status == Order.Status.NEW and not order["paid"]:
        builder.button(
            text=t("btn_cancel_order"),
            callback_data=MyOrdersCallback(action="cancel", order_id=order_id),
        )

    if status in (Order.Status.DELIVERED, Order.Status.CANCELLED):
        builder.button(text=t("btn_order_again"), callback_data=BackToCategories())

    builder.button(
        text=t("btn_to_list"),
        callback_data=MyOrdersCallback(action="list"),
    )

    builder.adjust(1)
    return builder.as_markup()


def cancel_confirm_keyboard(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=t("btn_yes_cancel"),
        callback_data=MyOrdersCallback(
            action="cancel_confirm", order_id=order_id
        ),
    )
    builder.button(
        text=t("btn_no_keep"),
        callback_data=MyOrdersCallback(
            action="cancel_abort", order_id=order_id
        ),
    )

    builder.adjust(1)
    return builder.as_markup()


def back_to_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t("btn_to_order"),
        callback_data=MyOrdersCallback(action="view", order_id=order_id),
    )
    return builder.as_markup()


def after_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn_catalog"), callback_data=BackToCategories())
    builder.adjust(1)
    return builder.as_markup()
