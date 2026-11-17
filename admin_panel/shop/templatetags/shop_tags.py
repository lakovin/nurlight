from decimal import Decimal

from django import template

register = template.Library()

DRINK_WORDS = ("напит", "сусын", "drink")


@register.filter
def money(value):
    """2900.00 → «2 900 ₸» (с неразрывными пробелами)."""
    value = Decimal(value or 0)
    text = f"{value:,.0f}" if value == value.to_integral() else f"{value:,.2f}"
    return text.replace(",", " ") + " ₸"


@register.filter
def times(value, count):
    return Decimal(value or 0) * int(count)


@register.filter
def product_icon(category):
    """Иконка вместо фото товара: напиток или блюдо — по названию категории."""
    name = (getattr(category, "name", "") or "").lower()
    return "drink" if any(word in name for word in DRINK_WORDS) else "dish"


@register.filter
def plural_ru(count, forms):
    """{{ n|plural_ru:"товар,товара,товаров" }}"""
    one, few, many = forms.split(",")
    n = abs(int(count)) % 100
    if 10 < n < 20:
        return many
    n %= 10
    return one if n == 1 else few if 2 <= n <= 4 else many
