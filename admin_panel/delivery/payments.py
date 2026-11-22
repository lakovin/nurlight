"""Оплата заказов во встроенных платежах Telegram (провайдер — Stripe, тестовый режим).

Бот выставляет счёт (send_invoice) с payload = invoice_payload(order),
перед списанием Telegram спрашивает бота (pre_checkout_query) → check_before_payment,
после списания приходит successful_payment → mark_paid.

Функции синхронные (ORM Django): в боте вызывать через sync_to_async.
Сумма — в тиынах (тенге × 100), как требует Telegram.
"""
from decimal import Decimal

from django.utils import timezone

from .models import Order

CURRENCY = "KZT"
PAYLOAD_PREFIX = "order:"


def amount(total: Decimal) -> int:
    """Тенге → тиыны: 2 900 ₸ → 290000."""
    return int((total * 100).to_integral_value())


def invoice_payload(order: Order) -> str:
    return f"{PAYLOAD_PREFIX}{order.pk}"


def _order_id(payload: str) -> int | None:
    if not payload.startswith(PAYLOAD_PREFIX) or not payload[len(PAYLOAD_PREFIX):].isdigit():
        return None
    return int(payload[len(PAYLOAD_PREFIX):])


def check_before_payment(payload: str, telegram_id: int, total_amount: int, currency: str) -> str | None:
    """Проверка перед списанием. None — можно платить, иначе текст ошибки для клиента."""
    order_id = _order_id(payload)
    order = Order.objects.filter(pk=order_id, client__telegram_id=telegram_id).first() if order_id else None
    if order is None:
        return "Заказ не найден."
    if order.payment_status == Order.PaymentStatus.PAID:
        return "Этот заказ уже оплачен."
    if order.status == Order.Status.CANCELLED:
        return "Заказ отменён, оплата не нужна."
    if currency != CURRENCY or total_amount != amount(order.total):
        return "Сумма заказа изменилась. Откройте заказ и оплатите заново."
    return None


def mark_paid(payload: str, telegram_id: int, total_amount: int, currency: str,
              telegram_charge_id: str, provider_charge_id: str) -> bool:
    """Отмечает заказ оплаченным. True — отметили сейчас, False — не наш заказ или уже оплачен.

    Деньги к этому моменту уже списаны: даже если сумма не сошлась, заказ отмечаем,
    а расхождение пусть разберёт оператор (номера платежа сохраняются).
    """
    order_id = _order_id(payload)
    if order_id is None:
        return False
    now = timezone.now()
    # Условное обновление: повторное сообщение о платеже ничего не меняет
    updated = Order.objects.filter(
        pk=order_id,
        client__telegram_id=telegram_id,
        payment_status=Order.PaymentStatus.UNPAID,
    ).update(
        payment_status=Order.PaymentStatus.PAID,
        paid_at=now,
        telegram_charge_id=telegram_charge_id,
        provider_charge_id=provider_charge_id,
        updated_at=now,
    )
    return bool(updated)
