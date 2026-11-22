"""Оплата заказов во встроенных платежах Telegram (провайдер — Stripe, тестовый режим).

Два счёта на заказ:
  • за товары — payload "order:<id>", сразу после оформления заказа;
  • за доставку — payload "delivery:<id>", когда оператор указал стоимость доставки
    (бесплатно от 5 000 ₸ — тогда 0 и счёт не нужен).

Бот выставляет счёт (send_invoice) с payload из invoice_payload / delivery_invoice_payload,
перед списанием Telegram спрашивает бота (pre_checkout_query) → check_before_payment,
после списания приходит successful_payment → mark_paid. Обе функции понимают оба вида счёта.

Функции синхронные (ORM Django): в боте вызывать через sync_to_async.
Сумма — в тиынах (тенге × 100), как требует Telegram; минимум у Telegram ~518 ₸.
"""
from decimal import Decimal

from django.utils import timezone

from .models import Order

CURRENCY = "KZT"
ORDER = "order"
DELIVERY = "delivery"


def amount(total: Decimal) -> int:
    """Тенге → тиыны: 2 900 ₸ → 290000."""
    return int((total * 100).to_integral_value())


def invoice_payload(order: Order) -> str:
    return f"{ORDER}:{order.pk}"


def delivery_invoice_payload(order: Order) -> str:
    return f"{DELIVERY}:{order.pk}"


def delivery_due(order: Order) -> bool:
    """Нужно ли выставить счёт за доставку: цена назначена, больше нуля, ещё не оплачена."""
    return (
        order.delivery_price is not None
        and order.delivery_price > 0
        and order.delivery_paid_at is None
        and order.status != Order.Status.CANCELLED
    )


def _parse(payload: str) -> tuple[str, int] | tuple[None, None]:
    kind, _, order_id = payload.partition(":")
    if kind not in (ORDER, DELIVERY) or not order_id.isdigit():
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
    if kind == ORDER:
        if order.payment_status == Order.PaymentStatus.PAID:
            return "Этот заказ уже оплачен."
        expected = amount(order.total)
    else:
        if order.delivery_paid_at is not None:
            return "Доставка уже оплачена."
        if not order.delivery_price:
            return "Стоимость доставки ещё не назначена — её укажет оператор."
        expected = amount(order.delivery_price)
    if currency != CURRENCY or total_amount != expected:
        return "Сумма изменилась. Откройте заказ и оплатите заново."
    return None


def mark_paid(payload: str, telegram_id: int, total_amount: int, currency: str,
              telegram_charge_id: str, provider_charge_id: str) -> bool:
    """Отмечает оплату товаров или доставки. True — отметили сейчас, False — не наш заказ или уже оплачено.

    Деньги к этому моменту уже списаны: даже если сумма не сошлась, оплату отмечаем,
    а расхождение пусть разберёт оператор (номера платежа сохраняются).
    """
    kind, order_id = _parse(payload)
    if kind is None:
        return False
    now = timezone.now()
    orders = Order.objects.filter(pk=order_id, client__telegram_id=telegram_id)
    # Условное обновление: повторное сообщение о платеже ничего не меняет
    if kind == ORDER:
        updated = orders.filter(payment_status=Order.PaymentStatus.UNPAID).update(
            payment_status=Order.PaymentStatus.PAID,
            paid_at=now,
            telegram_charge_id=telegram_charge_id,
            provider_charge_id=provider_charge_id,
            updated_at=now,
        )
    else:
        updated = orders.filter(delivery_paid_at__isnull=True).update(
            delivery_paid_at=now,
            delivery_telegram_charge_id=telegram_charge_id,
            delivery_provider_charge_id=provider_charge_id,
            updated_at=now,
        )
    return bool(updated)
