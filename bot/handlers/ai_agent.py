
import html
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.main_menu import main_menu
from bot.services.ai_agent import ask_ai

router = Router()
logger = logging.getLogger(__name__)

AI_BUTTON = "🤖 AI-помощник"


@router.message(Command("ai"))
@router.message(F.text == AI_BUTTON)
async def start_ai(message: Message, state: FSMContext):
    """Включает режим AI-консультанта."""

    await state.update_data(ai_enabled=True)

    await message.answer(
        "🤖 <b>Привет! Я AI-помощник Nurlight!</b>\n\n"
        "Могу помочь выбрать товары, "
        "подсказать цены и объяснить, "
        "как оформить заказ.\n\n"
        "Например, напиши:\n"
        "«Что у вас есть в меню?»\n\n"
        "Чтобы завершить общение, отправь /exit."
    )


@router.message(Command("exit"))
async def stop_ai(message: Message, state: FSMContext):
    """Выключает AI-режим."""

    await state.update_data(ai_enabled=False)

    await message.answer(
        "✅ AI-помощник отключён.\n"
        "Можешь пользоваться обычным меню.",
        reply_markup=main_menu,
    )


@router.message(F.text)
async def ai_chat(message: Message, state: FSMContext):
    """Обрабатывает сообщения пользователя."""

    data = await state.get_data()

    if not data.get("ai_enabled"):
        return

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing",
    )

    try:
        answer = await ask_ai(message.text)

        await message.answer(
            html.escape(answer[:4000])
        )

    except Exception:
        logger.exception("Ошибка Gemini AI")

        await message.answer(
            "⚠️ AI временно недоступен. "
            "Попробуйте позже."
        )
