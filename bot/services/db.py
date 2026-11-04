"""Подключение бота к моделям Django.

Бот и панель работают с одной базой, поэтому бот не описывает таблицы сам,
а использует модели из admin_panel/delivery через ORM Django.
"""
import os
import sys
from pathlib import Path

import django

ADMIN_PANEL_DIR = Path(__file__).resolve().parents[2] / "admin_panel"


def setup_django():
    if str(ADMIN_PANEL_DIR) not in sys.path:
        sys.path.insert(0, str(ADMIN_PANEL_DIR))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
