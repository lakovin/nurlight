"""Оплата заказов во встроенных платежах Telegram (провайдер — Stripe, тестовый режим).

Один счёт на заказ: сумма блюд + доставка (Order.total), payload "order:<id>".

Бот выставляет счёт (send_invoice) с payload из invoice_payload,
перед списанием Telegram спрашивает бота (pre_checkout_query) → check_before_payment,
после списания приходит successful_payment → mark_paid.

Функции синхронные (ORM Django): в боте вызывать через sync_to_async.
Сумма — в тиынах (тенге × 100), как требует Telegram; минимум у Telegram ~518 ₸.
"""
from decimal import Decimal

from django.utils import timezone

from .models import Order

CURRENCY = "KZT"
ORDER = "order"


def amount(total: Decimal) -> int:
    """Тенге → тиыны: 2 900 ₸ → 290000."""
    return int((total * 100).to_integral_value())


def invoice_payload(order: Order) -> str:
    return f"{ORDER}:{order.pk}"


def _parse(payload: str) -> tuple[str, int] | tuple[None, None]:
    kind, _, order_id = payload.partition(":")
    if kind != ORDER or not order_id.isdigit():
        return None, None
    return kind, int(order_id)


def check_before_payment(payload: str, telegram_id: int, total_amount: int, currency: str) -> str | None:
    """Проверка перед списанием. None — можно платить, иначе текст ошибки для клиента."""
    kind, order_id = _parse(payload)
    order = Order.objects.filter(pk=order_id, client__telegram_id=telegram_id).first() if order_id else None
    if order is None:
        return "Заказ не найден."
    if order.status == Order.Status.CANCELLED:
        return "Заказ отменён, оплата не нужна."
    if order.payment_status == Order.PaymentStatus.PAID:
        return "Этот заказ уже оплачен."
    expected = amount(order.total)
    if currency != CURRENCY or total_amount != expected:
        return "Сумма изменилась. Откройте заказ и оплатите заново."
    return None


def mark_paid(payload: str, telegram_id: int, total_amount: int, currency: str,
              telegram_charge_id: str, provider_charge_id: str) -> bool:
    """Отмечает заказ оплаченным. True — отметили сейчас, False — не наш заказ или уже оплачен.

    Деньги к этому моменту уже списаны: даже если сумма не сошлась, оплату отмечаем,
    а расхождение пусть разберёт оператор (номера платежа сохраняются).
    """
    kind, order_id = _parse(payload)
    if kind is None:
        return False
    now = timezone.now()
    orders = Order.objects.filter(pk=order_id, client__telegram_id=telegram_id)
    # Условное обновление: повторное сообщение о платеже ничего не меняет
    updated = orders.filter(payment_status=Order.PaymentStatus.UNPAID).update(
        payment_status=Order.PaymentStatus.PAID,
        paid_at=now,
        telegram_charge_id=telegram_charge_id,
        provider_charge_id=provider_charge_id,
        updated_at=now,
    )
    return bool(updated)
