"""Проверка переводов бота. Запуск из корня репозитория: python -m bot.tests_i18n

Проверяет:
1. у каждого ключа есть русский, казахский и английский текст;
2. плейсхолдеры {name} во всех языках одинаковые;
3. каждый t("ключ") в коде бота ссылается на существующий ключ;
4. в обработчиках и клавиатурах не осталось непереведённых русских строк
   (логи и docstring не считаются).
"""
import re
import string
import sys
import tokenize
from pathlib import Path

from bot.i18n import LANGS, TEXTS

ROOT = Path(__file__).resolve().parent


def placeholders(text: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def check_texts() -> list[str]:
    problems = []

    for key, versions in TEXTS.items():
        for lang in LANGS:
            if not versions.get(lang, "").strip():
                problems.append(f"{key}: нет перевода на {lang}")

        base = placeholders(versions.get("ru", ""))

        for lang in LANGS:
            if placeholders(versions.get(lang, "")) != base:
                problems.append(f"{key}: плейсхолдеры в {lang} отличаются от ru")

    return problems


def check_keys_used() -> list[str]:
    problems = []
    pattern = re.compile(r"""\bt\(\s*["']([a-z0-9_]+)["']""")
    keys_in_dicts = re.compile(r"""["'](notify_[a-z_]+)["']""")

    for path in ROOT.rglob("*.py"):
        if path.name in ("i18n.py", "tests_i18n.py"):
            continue

        text = path.read_text(encoding="utf-8")

        for key in pattern.findall(text) + keys_in_dicts.findall(text):
            if key not in TEXTS:
                problems.append(f"{path.relative_to(ROOT)}: нет ключа {key!r}")

    return problems


# Файлы, где русский текст — это логи, промпт AI или документация, а не ответ клиенту
SKIP_RUSSIAN_CHECK = {"i18n.py", "tests_i18n.py", "ai_agent.py", "db.py", "payments.py"}

# Русские строки, которые клиент не видит: записи в лог, служебные ошибки
# (они попадают в журнал, а не в чат) и контекст заказов для AI
INTERNAL_PREFIXES = (
    "Заказ %s",
    "Отмена чужого",
    "Ошибка при",
    "Заказ сохранён",
    "отправить подтверждение",
    "Платёж",
    "У клиента пока",
    "Уведомление по",
    "лимит Telegram",
    "Корзина пуста",  # ValueError в create_order
    "Клиент",  # имя по умолчанию, если у профиля его нет
    "Товар больше недоступен",  # ValueError в create_order
    "Неверное количество",  # ValueError в create_order
)


def check_hardcoded_russian() -> list[str]:
    problems = []
    cyrillic = re.compile("[А-Яа-яЁё]")

    for folder in ("handlers", "keyboards", "services"):
        for path in sorted((ROOT / folder).glob("*.py")):
            if path.name in SKIP_RUSSIAN_CHECK:
                continue

            with path.open("rb") as handle:
                previous_line = ""

                for token in tokenize.tokenize(handle.readline):
                    if token.type != tokenize.STRING or not cyrillic.search(token.string):
                        continue

                    if token.string.startswith(('"""', "'''")):
                        continue  # docstring

                    line = token.line.strip()
                    call = re.search(r"(logger|logging)\.\w+\(", token.line + previous_line)

                    if call or "logger." in line:
                        continue  # записи в лог остаются русскими

                    literal = token.string.lstrip("rbfRBF").strip("\"'")

                    if literal.startswith(INTERNAL_PREFIXES) or token.string.startswith(("r\"", "r'")):
                        continue  # служебные строки и регулярные выражения

                    problems.append(
                        f"{path.relative_to(ROOT)}:{token.start[0]}: {token.string[:70]}"
                    )

                    previous_line = token.line

    return problems


def main() -> int:
    sections = {
        "полнота переводов": check_texts(),
        "ключи в коде": check_keys_used(),
        "непереведённые строки": check_hardcoded_russian(),
    }

    failed = False

    for title, problems in sections.items():
        if problems:
            failed = True
            print(f"✗ {title}:")
            for problem in problems:
                print("   ", problem)
        else:
            print(f"✓ {title}")

    print(f"\nключей: {len(TEXTS)}, языков: {len(LANGS)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
