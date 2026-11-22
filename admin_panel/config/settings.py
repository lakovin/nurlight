from decimal import Decimal
from pathlib import Path
import os

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = BASE_DIR.parent

# Один .env в корне репозитория — общий для бота и панели
load_dotenv(REPO_DIR / ".env")

DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or ("dev-insecure-key" if DEBUG else None)
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY обязателен при DJANGO_DEBUG=0")
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
# Для работы через HTTPS-домен, например https://nurlight.moji.rest
CSRF_TRUSTED_ORIGINS = [o for o in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o]

if not DEBUG:
    # HTTPS завершается на Cloudflare, до Django запрос доходит по HTTP через туннель
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "delivery",
    "shop",
]

# Клиентский сайт-магазин (приложение shop) выключен: заказы принимает бот. 1 — включить обратно
SHOP_ENABLED = os.getenv("SHOP_ENABLED", "0") == "1"

# Контакты на сайте для клиентов; пустое значение — блок не показывается
SHOP = {
    "phone": os.getenv("SHOP_PHONE", ""),
    "hours": os.getenv("SHOP_HOURS", ""),
    "bot_username": os.getenv("TELEGRAM_BOT_USERNAME", "").lstrip("@"),
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Язык панели: русский, казахский, английский (переключатель в шапке админки)
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Свои шаблоны проекта — раньше шаблонов приложений (переключатель языка в admin/base_site.html)
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "shop.context_processors.shop",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Доставка: фиксированная цена, бесплатно от порога (входит в сумму заказа, Order.recalculate_total)
DELIVERY = {
    "fee": Decimal(os.getenv("DELIVERY_FEE", "500")),
    "free_from": Decimal(os.getenv("DELIVERY_FREE_FROM", "5000")),
}

# Пути SQLite в DATABASE_URL считаются от корня репозитория
_db_url = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
if _db_url.startswith("sqlite:///") and not _db_url.startswith("sqlite:////"):
    _db_url = f"sqlite:///{REPO_DIR / _db_url.removeprefix('sqlite:///')}"
# DB_PERSISTENT=1 — держать соединение с базой открытым между запросами (быстрый режим).
# С облачной базой новое подключение стоит ~2 с, повторное использование — ~0,1 с.
# Перед каждым запросом соединение проверяется, так что после сна базы сайт просто переподключится.
# Переключается командой deploy/db_mode.sh on|off.
DB_PERSISTENT = os.getenv("DB_PERSISTENT", "0") == "1"
DATABASES = {
    "default": dj_database_url.parse(
        _db_url,
        conn_max_age=600 if DB_PERSISTENT else 0,
        conn_health_checks=DB_PERSISTENT,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru"
LANGUAGES = [
    ("ru", "Русский"),
    ("kk", "Қазақша"),
    ("en", "English"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Asia/Almaty"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Сжатые файлы с хешем в имени нужны только в боевом режиме, после collectstatic
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        if DEBUG
        else "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
