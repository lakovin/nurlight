from bot.i18n import DEFAULT_LANG, LANGS
from delivery.models import Client

# Кэш языков: telegram_id -> язык, чтобы не ходить в базу на каждое сообщение
_cache: dict[int, str] = {}


async def get_language(telegram_id: int) -> str:
    """Язык клиента из Client.language (по умолчанию русский)."""

    if telegram_id in _cache:
        return _cache[telegram_id]

    language = await (
        Client.objects
        .filter(telegram_id=telegram_id)
        .values_list("language", flat=True)
        .afirst()
    )

    if language is None:
        # Клиента ещё нет в базе: не кэшируем, чтобы после регистрации прочитать язык
        return DEFAULT_LANG

    language = language if language in LANGS else DEFAULT_LANG
    _cache[telegram_id] = language
    return language


async def set_language(telegram_id: int, language: str) -> None:
    """Сохраняет выбранный язык в профиле клиента."""

    if language not in LANGS:
        return

    await Client.objects.filter(telegram_id=telegram_id).aupdate(language=language)
    _cache[telegram_id] = language
