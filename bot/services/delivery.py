from decimal import Decimal

from bot.services.validation import format_money

# Правило доставки (ответ Ислама, 21.11.2026): бесплатно от 5 000 ₸,
# иначе цена зависит от расстояния. Расчёт по расстоянию пока не
# реализован (нужны координаты и поле в заказе), поэтому при меньшей
# сумме стоимость называет оператор.
FREE_DELIVERY_FROM = Decimal("5000")


def delivery_line(total: Decimal | int | float) -> str:
    """Строка про доставку для сводки и карточки заказа."""

    if total >= FREE_DELIVERY_FROM:
        return "Доставка: бесплатно"

    return (
        "Доставка: стоимость уточнит оператор "
        f"(бесплатно от {format_money(FREE_DELIVERY_FROM)})"
    )
