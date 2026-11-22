"""Оплата в боте: счета во встроенных платежах Telegram.

Логика проверок и отметки оплаты — admin_panel/delivery/payments.py.
Здесь только выставление счетов.

Режимы (переменные .env):
- PAYMENT_PROVIDER_TOKEN задан — настоящие счета Telegram (тестовый или
  боевой токен от @BotFather);
- токена нет, но PAYMENT_DEMO=1 — демо: кнопка «Оплатить (тест)» отмечает
  заказ оплаченным БЕЗ списания денег (для показа на защите; не включать
  там, где оформляют настоящие заказы);
- ничего не задано — оплата выключена, бот работает как раньше.
"""
import os
import uuid
from decimal import Decimal

from aiogram.types import LabeledPrice, Message
from asgiref.sync import sync_to_async

from bot.keyboards.payment import demo_pay_keyboard
from bot.services.validation import format_money
from delivery import payments
from delivery.models import Order


def provider_token() -> str:
    return os.getenv("PAYMENT_PROVIDER_TOKEN", "")


def enabled() -> bool:
    """Настоящие счета Telegram включены."""
    return bool(provider_token())


def demo_enabled() -> bool:
    """Демо-оплата: только если нет настоящего токена."""
    return not enabled() and os.getenv("PAYMENT_DEMO") == "1"


def available() -> bool:
    """Оплата в боте доступна (настоящая или демо)."""
    return enabled() or demo_enabled()


def can_invoice(amount_kzt: Decimal) -> bool:
    """Telegram не принимает платёж меньше минимума (518 ₸)."""
    return available() and amount_kzt >= Order.MIN_INVOICE


async def send_order_invoice(
    message: Message,
    order_id: int,
    number: str,
    total: Decimal,
) -> bool:
    """Счёт за товары. False — счёт не выставлен (оплата выключена или сумма мала)."""

    if not can_invoice(total):
        return False

    if demo_enabled():
        await _send_demo(
            message,
            payments.ORDER,
            order_id,
            f"заказа №{number}",
            total,
        )
        return True

    await message.answer_invoice(
        title=f"Заказ №{number}",
        description="Оплата заказа Nurlight",
        payload=f"{payments.ORDER}:{order_id}",
        provider_token=provider_token(),
        currency=payments.CURRENCY,
        prices=[LabeledPrice(label="Заказ", amount=payments.amount(total))],
    )
    return True


async def send_delivery_invoice(
    message: Message,
    order_id: int,
    number: str,
    delivery_price: Decimal,
) -> bool:
    """Отдельный счёт за доставку (цену назначил оператор)."""

    if not can_invoice(delivery_price):
        return False

    if demo_enabled():
        await _send_demo(
            message,
            payments.DELIVERY,
            order_id,
            f"доставки заказа №{number}",
            delivery_price,
        )
        return True

    await message.answer_invoice(
        title=f"Доставка заказа №{number}",
        description="Оплата доставки Nurlight",
        payload=f"{payments.DELIVERY}:{order_id}",
        provider_token=provider_token(),
        currency=payments.CURRENCY,
        prices=[
            LabeledPrice(
                label="Доставка",
                amount=payments.amount(delivery_price),
            )
        ],
    )
    return True


async def _send_demo(
    message: Message,
    kind: str,
    order_id: int,
    what: str,
    amount_kzt: Decimal,
) -> None:
    await message.answer(
        f"💳 <b>Тестовая оплата {what}</b>\n"
        f"Сумма: {format_money(amount_kzt)}\n\n"
        "Это демонстрационный режим: деньги не списываются.",
        reply_markup=demo_pay_keyboard(kind, order_id),
    )


def _demo_pay_sync(telegram_id: int, kind: str, order_id: int) -> str | None:
    if kind not in (payments.ORDER, payments.DELIVERY):
        return "Заказ не найден."

    order = Order.objects.filter(
        pk=order_id, client__telegram_id=telegram_id
    ).first()

    if order is None:
        return "Заказ не найден."

    total = (
        order.total
        if kind == payments.ORDER
        else (order.delivery_price or Decimal(0))
    )
    amount = payments.amount(total)
    payload = f"{kind}:{order_id}"

    # Те же проверки, что и у настоящей оплаты
    error = payments.check_before_payment(
        payload, telegram_id, amount, payments.CURRENCY
    )

    if error:
        return error

    charge = f"demo-{uuid.uuid4().hex[:12]}"
    payments.mark_paid(
        payload, telegram_id, amount, payments.CURRENCY, charge, charge
    )
    return None


async def demo_pay(telegram_id: int, kind: str, order_id: int) -> str | None:
    """Демо-оплата. None — успех, иначе текст ошибки для клиента."""
    return await sync_to_async(_demo_pay_sync)(telegram_id, kind, order_id)
