import re


def normalize_phone(raw: str) -> str | None:
    """Приводит казахстанский номер к виду +7XXXXXXXXXX; None, если это не номер."""
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 11 and digits[0] == "8":
        digits = "7" + digits[1:]
    elif len(digits) == 10:
        digits = "7" + digits
    if len(digits) != 11 or digits[0] != "7":
        return None
    return "+" + digits
