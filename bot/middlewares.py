from aiogram import BaseMiddleware, Dispatcher
from asgiref.sync import sync_to_async
from django.db import close_old_connections

from bot.i18n import DEFAULT_LANG, current_lang
from bot.services import notifications
from bot.services.language import get_language


class DatabaseMiddleware(BaseMiddleware):
    """Убирает оборванное соединение с базой перед каждым обновлением.

    В сайте это делает сам Django, а в боте нет запросов HTTP: без этого после
    обрыва (сон Neon, сбой сети) все обработчики падали бы до перезапуска.
    """

    async def __call__(self, handler, event, data):
        await sync_to_async(close_old_connections)()

        try:
            return await handler(event, data)
        finally:
            # База уже разбужена клиентом: заодно проверим статусы заказов
            notifications.wake()


class LanguageMiddleware(BaseMiddleware):
    """Определяет язык клиента и кладёт его в current_lang.

    После этого в любом обработчике t("ключ") возвращает текст на языке клиента.
    """

    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")

        language = DEFAULT_LANG

        if user is not None:
            try:
                language = await get_language(user.id)
            except Exception:
                # База недоступна — отвечаем на русском, а не падаем
                language = DEFAULT_LANG

        current_lang.set(language)

        return await handler(event, data)


def register(dp: Dispatcher) -> None:
    """Подключает определение языка к сообщениям и нажатиям кнопок."""
    dp.update.outer_middleware(DatabaseMiddleware())

    middleware = LanguageMiddleware()

    dp.message.outer_middleware(middleware)
    dp.callback_query.outer_middleware(middleware)
    dp.pre_checkout_query.outer_middleware(middleware)
