import html
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.i18n import t
from bot.keyboards.main_menu import MY_ORDERS_BUTTONS
from bot.keyboards.my_orders import (
    MyOrdersCallback,
    after_cancel_keyboard,
    back_to_order_keyboard,
    cancel_confirm_keyboard,
    empty_orders_keyboard,
    order_card_keyboard,
    orders_list_keyboard,
    retry_list_keyboard,
)
from bot.services.delivery import delivery_text
from bot.services.notifications import mark_known
from bot.services.payment import (
    available as payment_enabled,
    send_order_invoice,
)
from bot.services.my_orders import (
    ORDERS_LIMIT,
    cancel_by_client,
    client_order_number,
    get_last_orders,
    get_order_for_client,
)
from bot.services.validation import format_money, format_phone
from delivery.models import Order


router = Router()
logger = logging.getLogger(__name__)

# ---------- Тексты ----------

def format_orders(orders: list[dict]) -> str:
    """Текст списка заказов."""
    lines = [t("orders_title"), ""]

    for index, order in enumerate(orders, start=1):
        lines.append(
            f"{index}. №{order['number']} — {order['status_text']} — "
            f"{format_money(order['total'])} — "
            f"{order['created']:%d.%m, %H:%M}"
        )

    if len(orders) >= ORDERS_LIMIT:
        lines.extend(["", t("orders_limit", n=ORDERS_LIMIT)])

    return "\n".join(lines)


def format_order_card(order: dict) -> str:
    """Текст карточки заказа. Цены — из OrderItem."""
    lines = [
        t("card_title", number=order["number"]),
        t("card_status", status=order["status_text"]),
        t("card_created", date=f"{order['created']:%d.%m.%Y, %H:%M}"),
        "",
        t("card_items_header"),
    ]

    for item in order["items"]:
        subtotal = item["price"] * item["quantity"]
        lines.append(
            f"• {html.escape(item['name'])} — {item['quantity']} × "
            f"{format_money(item['price'])} = {format_money(subtotal)}"
        )

    phone = format_phone(order["phone"]) if order["phone"] else "—"
    comment = order["comment"] or "—"

    lines.extend([
        "",
        t("label_items", amount=format_money(order["items_total"])),
        delivery_text(order["delivery_fee"]),
        t("label_total", amount=format_money(order["total"])),
        *(
            [
                t(
                    "card_payment",
                    state=t("pay_state_paid" if order["paid"] else "pay_state_unpaid"),
                )
            ]
            if order["paid"] or payment_enabled()
            else []
        ),
        "",
        *(
            [
                t(
                    "summary_location",
                    url=(
                        "https://www.google.com/maps?q="
                        f"{order['latitude']},{order['longitude']}"
                    ),
                )
            ]
            if order["latitude"] is not None
            else []
        ),
        t("card_note", text=html.escape(order["address"] or "—")),
        t("card_phone", text=html.escape(phone)),
        t("card_comment", text=html.escape(comment)),
    ])

    if order["status"] == "delivered":
        lines.extend(["", t("delivered_thanks")])

    return "\n".join(lines)


# ---------- Список ----------

async def show_list(target: Message | CallbackQuery) -> None:
    """Показывает список заказов: новым сообщением или правкой карточки."""
    message = target if isinstance(target, Message) else target.message

    try:
        orders = await get_last_orders(target.from_user.id)
    except Exception:
        logger.exception("Не удалось загрузить заказы")
        text, markup = t("orders_load_error"), retry_list_keyboard()
    else:
        if orders:
            text = format_orders(orders)
            markup = orders_list_keyboard(orders)
        else:
            text, markup = t("orders_empty"), empty_orders_keyboard()

    if isinstance(target, Message):
        await message.answer(text, reply_markup=markup)
    else:
        await message.edit_text(text, reply_markup=markup)


@router.message(Command("orders"))
@router.message(F.text.in_(MY_ORDERS_BUTTONS))
async def show_orders(message: Message):
    await show_list(message)


@router.callback_query(MyOrdersCallback.filter(F.action == "list"))
async def back_to_list(callback: CallbackQuery):
    await show_list(callback)
    await callback.answer()


# ---------- Карточка ----------

async def load_card(callback: CallbackQuery, order_id: int) -> dict | None:
    """Загружает заказ; чужой или несуществующий — None и запись в лог."""
    order = await get_order_for_client(callback.from_user.id, order_id)

    if order is None:
        logger.warning(
            "Заказ %s не найден для пользователя %s",
            order_id,
            callback.from_user.id,
        )
        await callback.answer(t("order_not_found"), show_alert=True)

    return order


@router.callback_query(MyOrdersCallback.filter(F.action == "view"))
async def view_order(
    callback: CallbackQuery,
    callback_data: MyOrdersCallback,
):
    order = await load_card(callback, callback_data.order_id)

    if order is None:
        return

    await callback.message.edit_text(
        format_order_card(order),
        reply_markup=order_card_keyboard(order),
    )
    await callback.answer()


@router.callback_query(MyOrdersCallback.filter(F.action == "refresh"))
async def refresh_order(
    callback: CallbackQuery,
    callback_data: MyOrdersCallback,
):
    order = await load_card(callback, callback_data.order_id)

    if order is None:
        return

    try:
        await callback.message.edit_text(
            format_order_card(order),
            reply_markup=order_card_keyboard(order),
        )
    except TelegramBadRequest as error:
        # Текст и кнопки те же — статус не изменился
        if "message is not modified" not in str(error):
            raise

        await callback.answer(t("status_unchanged"))
        return

    await callback.answer(t("status_updated"))


# ---------- Оплата ----------

@router.callback_query(MyOrdersCallback.filter(F.action == "pay"))
async def pay_order(
    callback: CallbackQuery,
    callback_data: MyOrdersCallback,
):
    """Выставляет один счёт на весь заказ (блюда + доставка)."""

    order = await load_card(callback, callback_data.order_id)

    if order is None:
        return

    try:
        sent = (
            not order["paid"]
            and order["status"] != "cancelled"
            and await send_order_invoice(
                callback.message,
                order["id"],
                order["number"],
                order["items_total"],
                order["delivery_fee"],
            )
        )
    except Exception:
        logger.exception("Не удалось выставить счёт по заказу %s", order["id"])
        await callback.answer(
            t("invoice_failed"),
            show_alert=True,
        )
        return

    if not sent:
        await callback.answer(
            t("payment_unavailable"),
            show_alert=True,
        )
        return

    await callback.answer()


# ---------- Отмена ----------

@router.callback_query(MyOrdersCallback.filter(F.action == "cancel"))
async def ask_cancel(
    callback: CallbackQuery,
    callback_data: MyOrdersCallback,
):
    order = await load_card(callback, callback_data.order_id)

    if order is None:
        return

    if order["paid"] or order["status"] != "new":
        await callback.message.edit_text(
            t("cancel_paid") if order["paid"] else t("cancel_too_late"),
            reply_markup=back_to_order_keyboard(order["id"]),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        t(
            "cancel_ask",
            number=order["number"],
            amount=format_money(order["total"]),
        ),
        reply_markup=cancel_confirm_keyboard(order["id"]),
    )
    await callback.answer()


@router.callback_query(MyOrdersCallback.filter(F.action == "cancel_abort"))
async def abort_cancel(
    callback: CallbackQuery,
    callback_data: MyOrdersCallback,
):
    await view_order(callback, callback_data)


@router.callback_query(
    MyOrdersCallback.filter(F.action == "cancel_confirm")
)
async def confirm_cancel(
    callback: CallbackQuery,
    callback_data: MyOrdersCallback,
):
    order_id = callback_data.order_id

    try:
        result = await cancel_by_client(callback.from_user.id, order_id)
    except Exception:
        logger.exception("Ошибка отмены заказа %s", order_id)
        await callback.message.edit_text(
            t("cancel_failed"),
            reply_markup=back_to_order_keyboard(order_id),
        )
        await callback.answer()
        return

    if result == "cancelled":
        # Клиент сам отменил и видит подтверждение: без дубля уведомлением
        mark_known(order_id, Order.Status.CANCELLED)

        order = await get_order_for_client(callback.from_user.id, order_id)
        number = order["number"] if order else await client_order_number(order_id)

        await callback.message.edit_text(
            t("cancel_done", number=number),
            reply_markup=after_cancel_keyboard(),
        )
        await callback.answer()
        return

    if result == "already_cancelled":
        await callback.answer(t("already_cancelled"), show_alert=True)
        return

    if result in ("too_late", "paid"):
        await callback.message.edit_text(
            t("cancel_paid") if result == "paid" else t("cancel_too_late"),
            reply_markup=back_to_order_keyboard(order_id),
        )
        await callback.answer()
        return

    logger.warning(
        "Отмена чужого или несуществующего заказа %s пользователем %s",
        order_id,
        callback.from_user.id,
    )
    await callback.answer(t("order_not_found"), show_alert=True)
