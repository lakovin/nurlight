from aiogram import BaseMiddleware, Dispatcher

from bot.i18n import DEFAULT_LANG, current_lang
from bot.services.language import get_language


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
    middleware = LanguageMiddleware()

    dp.message.outer_middleware(middleware)
    dp.callback_query.outer_middleware(middleware)
    dp.pre_checkout_query.outer_middleware(middleware)
