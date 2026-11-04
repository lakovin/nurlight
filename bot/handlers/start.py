import html

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.main_menu import main_menu
from bot.services.clients import get_or_register_client

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    client = await get_or_register_client(user.id, user.full_name)
    await message.answer(
        f"Здравствуйте, {html.escape(client.name)}! 👋\n"
        "Я бот службы доставки Nurlight. Здесь можно выбрать товары и оформить заказ.",
        reply_markup=main_menu,
    )
