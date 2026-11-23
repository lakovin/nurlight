"""Автотесты бота. Запуск из корня репозитория:

    python -m unittest discover -s bot/tests -t . -v

Тесты работают на временной SQLite-базе (файл .test_bot.sqlite3 в корне, он
удаляется после запуска). Боевая база и ваш db.sqlite3 не затрагиваются.
"""
import atexit
import os
from pathlib import Path

TEST_DB_NAME = ".test_bot.sqlite3"

# Тесты не зависят от вашего .env (база, токены, цены доставки заданы здесь):
# настройки проекта читают .env, но не перезаписывают уже заданные переменные
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_NAME}"
os.environ["DELIVERY_FEE"] = "500"
os.environ["DELIVERY_FREE_FROM"] = "5000"
os.environ["PAYMENT_PROVIDER_TOKEN"] = ""  # пустое значение: токен из .env не подтянется
os.environ["PAYMENT_DEMO"] = "1"
os.environ["GEMINI_API_KEY"] = ""

from bot.services.db import setup_django  # noqa: E402

setup_django()

from django.conf import settings  # noqa: E402
from django.core.management import call_command  # noqa: E402

_db = settings.DATABASES["default"]

# Защита: тесты никогда не запускаются на боевой базе
assert "sqlite" in _db["ENGINE"] and str(_db["NAME"]).endswith(TEST_DB_NAME), (
    f"Тесты должны идти на временной SQLite, а не на {_db['ENGINE']}"
)

# Остаток прошлого запуска (Windows может не отдать файл сразу после тестов)
try:
    Path(str(_db["NAME"])).unlink(missing_ok=True)
except PermissionError:
    pass

call_command("migrate", verbosity=0)


def _cleanup() -> None:
    from django.db import connections

    connections.close_all()

    try:
        Path(str(_db["NAME"])).unlink(missing_ok=True)
    except OSError:
        pass  # файл удалится в начале следующего запуска; он в .gitignore


atexit.register(_cleanup)
