import re
from decimal import Decimal

from bot.i18n import t


def validate_address_note(note: str) -> str | None:
    """Проверяет необязательное уточнение адреса (подъезд, этаж, квартира)."""
    if len(note.strip()) > 500:
        return t("err_note_too_long")

    return None


def normalize_phone(raw: str) -> str | None:
    """Приводит казахстанский номер к формату +7XXXXXXXXXX."""
    if re.search(r"[A-Za-zА-Яа-я]", raw):
        return None

    digits = re.sub(r"\D", "", raw)

    if len(digits) == 10:
        digits = "7" + digits
    elif len(digits) == 11 and digits[0] in "78":
        digits = "7" + digits[1:]
    else:
        return None

    return "+" + digits


def validate_comment(comment: str) -> str | None:
    """Проверяет длину комментария."""
    if len(comment.strip()) > 500:
        return t("err_comment_too_long")

    return None


def format_phone(phone: str) -> str:
    """Форматирует номер телефона для отображения."""
    digits = re.sub(r"\D", "", phone)

    if len(digits) == 11 and digits.startswith("7"):
        return (
            f"+7 {digits[1:4]} {digits[4:7]} "
            f"{digits[7:9]} {digits[9:11]}"
        )

    return phone


def format_money(value: Decimal | int | float) -> str:
    """Форматирует сумму в тенге."""
    return f"{value:,.0f}".replace(",", "\u00a0") + " ₸"
