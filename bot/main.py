import asyncio
import logging
import os

from bot.services.db import setup_django

# Подключаем Django перед импортом обработчиков
setup_django()

from aiogram import Bot, Dispatcher  # noqa: E402
from aiogram.client.default import DefaultBotProperties  # noqa: E402
from aiogram.enums import ParseMode  # noqa: E402

from bot.handlers import (  # noqa: E402
    ai_agent,
    cart,
    catalog,
    faq,
    my_orders,
    order,
    start,
)


async def main():
    logging.basicConfig(level=logging.INFO)

    token = os.getenv("BOT_TOKEN")

    if not token:
        raise SystemExit(
            "BOT_TOKEN не задан. Проверьте файл .env"
        )

    bot = Bot(
        token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        ),
    )

    dp = Dispatcher()

    # AI-обработчик ставим последним
    dp.include_routers(
        order.router,
        my_orders.router,
        faq.router,
        start.router,
        catalog.router,
        cart.router,
        ai_agent.router,
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())