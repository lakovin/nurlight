import asyncio
import logging
import os

from bot.services.db import setup_django

# Django нужно настроить до импорта обработчиков: они используют модели
setup_django()

from aiogram import Bot, Dispatcher  # noqa: E402
from aiogram.client.default import DefaultBotProperties  # noqa: E402
from aiogram.enums import ParseMode  # noqa: E402

from bot.handlers import catalog, start  # noqa: E402


async def main():
    logging.basicConfig(level=logging.INFO)
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("BOT_TOKEN не задан — скопируйте .env.example в .env и укажите токен")

    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_routers(start.router, catalog.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
