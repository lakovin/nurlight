from decimal import Decimal

from bot.services.validation import format_money

# Правило доставки (ответ Ислама, 21.11.2026): бесплатно от 5 000 ₸,
# иначе цена зависит от расстояния. Расчёт по расстоянию пока не
# реализован (нужны координаты и поле в заказе), поэтому при меньшей
# сумме стоимость называет оператор.
FREE_DELIVERY_FROM = Decimal("5000")


def order_delivery_line(
    total: Decimal,
    delivery_price: Decimal | None,
    delivery_paid: bool,
) -> str:
    """Строка про доставку в карточке заказа с учётом цены оператора."""

    if delivery_price is None:
        # Оператор ещё не назначил цену: действует правило порога
        return delivery_line(total)

    if delivery_price == 0:
        return "Доставка: бесплатно"

    state = "оплачена" if delivery_paid else "ожидает оплаты"
    return f"Доставка: {format_money(delivery_price)} ({state})"


def delivery_line(total: Decimal | int | float) -> str:
    """Строка про доставку для сводки и карточки заказа."""

    if total >= FREE_DELIVERY_FROM:
        return "Доставка: бесплатно"

    return (
        "Доставка: стоимость уточнит оператор "
        f"(бесплатно от {format_money(FREE_DELIVERY_FROM)})"
    )
