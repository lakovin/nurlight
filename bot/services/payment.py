"""Оплата в боте: один счёт на заказ (блюда + доставка) во встроенных платежах Telegram.

Логика проверок и отметки оплаты — admin_panel/delivery/payments.py.
Здесь только выставление счёта.

Режимы (переменные .env):
- PAYMENT_PROVIDER_TOKEN задан — настоящие счета Telegram (тестовый или
  боевой токен от @BotFather);
- токена нет, но PAYMENT_DEMO=1 — демо: кнопка «Оплатить (тест)» отмечает
  заказ оплаченным БЕЗ списания денег (для показа на защите; не включать
  там, где оформляют настоящие заказы). Если задан и PAYMENT_DEMO_URL (https),
  вместо кнопки открывается окно с тестовой картой (страница landing/pay);
- ничего не задано — оплата выключена, бот работает как раньше.
"""
import json
import os
import uuid
from decimal import Decimal
from urllib.parse import urlencode

from aiogram.types import LabeledPrice, Message
from asgiref.sync import sync_to_async

from bot.i18n import current_lang, t
from bot.keyboards.payment import demo_pay_keyboard, demo_window_keyboard
from bot.services.validation import format_money
from delivery import payments
from delivery.models import Order

# Минимальный платёж в Telegram для тенге
MIN_INVOICE = Decimal("518")


def provider_token() -> str:
    return os.getenv("PAYMENT_PROVIDER_TOKEN", "")


def enabled() -> bool:
    """Настоящие счета Telegram включены."""
    return bool(provider_token())


def demo_enabled() -> bool:
    """Демо-оплата: только если нет настоящего токена."""
    return not enabled() and os.getenv("PAYMENT_DEMO") == "1"


def demo_window_url(order_id: int, number: str, total: Decimal) -> str | None:
    """Адрес окна тестовой оплаты. None — страница не задана (Telegram требует https)."""
    base = os.getenv("PAYMENT_DEMO_URL", "").strip()

    if not base.startswith("https://"):
        return None

    return base + "?" + urlencode({
        "o": order_id,
        "n": number,
        "sum": format_money(total),
        "lang": current_lang.get(),
    })


def parse_window_data(data: str) -> tuple[int, str] | None:
    """Ответ окна оплаты → (id заказа, "ok" или "declined"). None — непонятные данные."""
    try:
        parsed = json.loads(data)
    except ValueError:
        return None

    if not isinstance(parsed, dict):
        return None

    order_id, result = parsed.get("order"), parsed.get("result")

    # type(), а не isinstance: True — тоже int
    if type(order_id) is not int or not 0 < order_id < 2**63:
        return None

    if result not in ("ok", "declined"):
        return None

    return order_id, result


def available() -> bool:
    """Оплата в боте доступна (настоящая или демо)."""
    return enabled() or demo_enabled()


def can_invoice(total: Decimal) -> bool:
    """Оплата включена и сумма не меньше минимума Telegram."""
    return available() and total >= MIN_INVOICE


async def send_order_invoice(
    message: Message,
    order_id: int,
    number: str,
    items_total: Decimal,
    delivery_fee: Decimal,
) -> bool:
    """Выставляет счёт на весь заказ. False — не выставлен (оплата выключена или сумма мала).

    В счёте две строки (блюда и доставка), а сумма равна Order.total,
    её же проверяет payments.check_before_payment.
    """

    total = items_total + delivery_fee

    if not can_invoice(total):
        return False

    if demo_enabled():
        url = demo_window_url(order_id, number, total)
        text = t("demo_invoice", number=number, amount=format_money(total))

        if url:
            text += "\n\n" + t("demo_window_hint")
            keyboard = demo_window_keyboard(url)
        else:
            keyboard = demo_pay_keyboard(order_id)

        await message.answer(text, reply_markup=keyboard)
        return True

    prices = [
        LabeledPrice(label=t("invoice_items"), amount=payments.amount(items_total))
    ]

    if delivery_fee > 0:
        prices.append(
            LabeledPrice(
                label=t("invoice_delivery"),
                amount=payments.amount(delivery_fee),
            )
        )

    await message.answer_invoice(
        title=t("invoice_title", number=number),
        description=t("invoice_desc"),
        payload=f"{payments.ORDER}:{order_id}",
        provider_token=provider_token(),
        currency=payments.CURRENCY,
        prices=prices,
    )
    return True


def _demo_pay_sync(telegram_id: int, order_id: int) -> str | None:
    order = Order.objects.filter(
        pk=order_id, client__telegram_id=telegram_id
    ).first()

    if order is None:
        return t("order_not_found")

    payload = payments.invoice_payload(order)
    amount = payments.amount(order.total)

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


async def demo_pay(telegram_id: int, order_id: int) -> str | None:
    """Демо-оплата. None — успех, иначе текст ошибки для клиента."""
    return await sync_to_async(_demo_pay_sync)(telegram_id, order_id)
