from decimal import Decimal

from django.conf import settings

from bot.services.validation import format_money


def rules() -> tuple[Decimal, Decimal]:
    """Правило доставки из настроек: (цена, порог бесплатной доставки).

    Те же настройки использует модель Order.recalculate_total, поэтому
    сумма в сводке бота совпадает с суммой заказа в базе.
    """
    return settings.DELIVERY["fee"], settings.DELIVERY["free_from"]


def delivery_fee_for(items_total: Decimal) -> Decimal:
    """Цена доставки для суммы блюд: бесплатно от порога, иначе фиксированная."""
    fee, free_from = rules()
    return Decimal(0) if items_total >= free_from else fee


def delivery_text(fee: Decimal) -> str:
    """Строка про доставку для сводки и карточки заказа."""

    if fee == 0:
        return "Доставка: бесплатно"

    _, free_from = rules()
    return f"Доставка: {format_money(fee)} (бесплатно от {format_money(free_from)})"
