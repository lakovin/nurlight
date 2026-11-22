import html
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards.main_menu import MY_ORDERS_BUTTON
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
from bot.services.delivery import order_delivery_line
from bot.services.notifications import mark_known
from bot.services.payment import (
    available as payment_enabled,
    send_delivery_invoice,
    send_order_invoice,
)
from bot.services.my_orders import (
    ORDERS_LIMIT,
    cancel_by_client,
    get_last_orders,
    get_order_for_client,
)
from bot.services.validation import format_money, format_phone
from delivery.models import Order


router = Router()
logger = logging.getLogger(__name__)

EMPTY_TEXT = "Пока нет заказов. Самое время что-нибудь выбрать 🛍"
LOAD_ERROR_TEXT = "Не удалось загрузить заказы. Попробуйте ещё раз."
NOT_FOUND_TEXT = "Заказ не найден."
TOO_LATE_TEXT = (
    "Заказ уже принят оператором — отменить его нельзя.\n"
    "Свяжитесь с оператором, он поможет."
)
PAID_TEXT = (
    "Заказ уже оплачен. Отмену и возврат денег оформит оператор.\n"
    "Свяжитесь с оператором, он поможет."
)


# ---------- Тексты ----------

def format_orders(orders: list[dict]) -> str:
    """Текст списка заказов."""
    lines = ["<b>📦 Мои заказы</b>", ""]

    for index, order in enumerate(orders, start=1):
        lines.append(
            f"{index}. №{order['number']} — {order['status_text']} — "
            f"{format_money(order['total'])} — "
            f"{order['created']:%d.%m, %H:%M}"
        )

    if len(orders) >= ORDERS_LIMIT:
        lines.extend(["", f"Показаны последние {ORDERS_LIMIT} заказов."])

    return "\n".join(lines)


def format_order_card(order: dict) -> str:
    """Текст карточки заказа. Цены — из OrderItem."""
    lines = [
        f"<b>📦 Заказ №{order['number']}</b>",
        f"Статус: {order['status_text']}",
        f"Создан: {order['created']:%d.%m.%Y, %H:%M}",
        "",
        "Состав:",
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
        f"Товары: {format_money(order['total'])}",
        order_delivery_line(
            order["total"],
            order["delivery_price"],
            order["delivery_paid"],
        ),
        f"<b>Итого: {format_money(order['total'])}</b>",
        *(
            [f"Оплата: {'✅ оплачен' if order['paid'] else 'не оплачен'}"]
            if order["paid"] or payment_enabled()
            else []
        ),
        "",
        f"Адрес: {html.escape(order['address'])}",
        f"Телефон: {html.escape(phone)}",
        f"Комментарий: {html.escape(comment)}",
    ])

    if order["status"] == "delivered":
        lines.extend(["", "🙏 Спасибо за заказ! Будем рады видеть снова."])

    return "\n".join(lines)


# ---------- Список ----------

async def show_list(target: Message | CallbackQuery) -> None:
    """Показывает список заказов: новым сообщением или правкой карточки."""
    message = target if isinstance(target, Message) else target.message

    try:
        orders = await get_last_orders(target.from_user.id)
    except Exception:
        logger.exception("Не удалось загрузить заказы")
        text, markup = LOAD_ERROR_TEXT, retry_list_keyboard()
    else:
        if orders:
            text = format_orders(orders)
            markup = orders_list_keyboard(orders)
        else:
            text, markup = EMPTY_TEXT, empty_orders_keyboard()

    if isinstance(target, Message):
        await message.answer(text, reply_markup=markup)
    else:
        await message.edit_text(text, reply_markup=markup)


@router.message(Command("orders"))
@router.message(F.text == MY_ORDERS_BUTTON)
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
        await callback.answer(NOT_FOUND_TEXT, show_alert=True)

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

        await callback.answer("Статус не изменился.")
        return

    await callback.answer("Статус обновлён")


# ---------- Оплата ----------

@router.callback_query(
    MyOrdersCallback.filter(F.action.in_({"pay", "pay_delivery"}))
)
async def pay_order(
    callback: CallbackQuery,
    callback_data: MyOrdersCallback,
):
    """Выставляет счёт: за товары или отдельно за доставку."""

    order = await load_card(callback, callback_data.order_id)

    if order is None:
        return

    try:
        if callback_data.action == "pay_delivery":
            sent = order["delivery_due"] and await send_delivery_invoice(
                callback.message,
                order["id"],
                order["number"],
                order["delivery_price"],
            )
        else:
            sent = (
                not order["paid"]
                and order["status"] != "cancelled"
                and await send_order_invoice(
                    callback.message,
                    order["id"],
                    order["number"],
                    order["total"],
                )
            )
    except Exception:
        logger.exception("Не удалось выставить счёт по заказу %s", order["id"])
        await callback.answer(
            "Не удалось выставить счёт. Попробуйте позже.",
            show_alert=True,
        )
        return

    if not sent:
        await callback.answer(
            "Оплата для этого заказа сейчас недоступна.",
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
            PAID_TEXT if order["paid"] else TOO_LATE_TEXT,
            reply_markup=back_to_order_keyboard(order["id"]),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"Отменить заказ №{order['number']} на "
        f"{format_money(order['total'])}?\n\n"
        "Если передумали — вернитесь к заказу.",
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
            "Не удалось отменить заказ. Попробуйте ещё раз "
            "или свяжитесь с оператором.",
            reply_markup=back_to_order_keyboard(order_id),
        )
        await callback.answer()
        return

    if result == "cancelled":
        # Клиент сам отменил и видит подтверждение: без дубля уведомлением
        mark_known(order_id, Order.Status.CANCELLED)

        order = await get_order_for_client(callback.from_user.id, order_id)
        number = order["number"] if order else f"{order_id:06d}"

        await callback.message.edit_text(
            f"Заказ №{number} отменён.\n\n"
            "Если что-то пошло не так, напишите оператору.",
            reply_markup=after_cancel_keyboard(),
        )
        await callback.answer()
        return

    if result == "already_cancelled":
        await callback.answer("Заказ уже отменён.", show_alert=True)
        return

    if result in ("too_late", "paid"):
        await callback.message.edit_text(
            PAID_TEXT if result == "paid" else TOO_LATE_TEXT,
            reply_markup=back_to_order_keyboard(order_id),
        )
        await callback.answer()
        return

    logger.warning(
        "Отмена чужого или несуществующего заказа %s пользователем %s",
        order_id,
        callback.from_user.id,
    )
    await callback.answer(NOT_FOUND_TEXT, show_alert=True)
