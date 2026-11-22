import html
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.main_menu import (
    AI_BUTTON,
    AI_BUTTON_LEGACY,
    main_menu,
)
from bot.services.ai_agent import (
    MAX_HISTORY_MESSAGES,
    ask_ai,
)
from bot.services.my_orders import get_orders_context


router = Router()
logger = logging.getLogger(__name__)


# ---------- Запуск AI-помощника ----------

@router.message(Command("ai"))
@router.message(F.text.in_({AI_BUTTON, AI_BUTTON_LEGACY}))
async def start_ai(
    message: Message,
    state: FSMContext,
):
    """Включает AI-помощника и начинает новый диалог."""

    await state.update_data(
        ai_enabled=True,
        ai_history=[],
    )

    await message.answer(
        "💬 <b>Виртуальный оператор Nurlight</b>\n\n"
        "Привет! 👋 Я бот-помощник: подскажу по меню и ценам, "
        "доставке и вашим заказам.\n\n"
        "Просто напиши, что тебя интересует!\n\n"
        "🧹 /clear — начать новый разговор\n"
        "❌ /exit — завершить диалог"
    )


# ---------- Очистка памяти AI ----------

@router.message(Command("clear"))
async def clear_ai_memory(
    message: Message,
    state: FSMContext,
):
    """Удаляет историю предыдущих сообщений."""

    await state.update_data(
        ai_history=[],
    )

    await message.answer(
        "🧹 <b>Память AI очищена!</b>\n\n"
        "Можем начать разговор заново."
    )


# ---------- Выход из AI ----------

@router.message(Command("exit"))
async def stop_ai(
    message: Message,
    state: FSMContext,
):
    """Завершает AI-диалог и очищает историю."""

    await state.update_data(
        ai_enabled=False,
        ai_history=[],
    )

    await message.answer(
        "✅ AI-диалог завершён.\n"
        "Можешь пользоваться обычным меню.",
        reply_markup=main_menu,
    )


# ---------- Общение с AI ----------

@router.message(F.text)
async def ai_chat(
    message: Message,
    state: FSMContext,
):
    """Отправляет вопрос Gemini с историей разговора."""

    data = await state.get_data()

    # AI выключен — ничего не делаем
    if not data.get("ai_enabled"):
        return

    history = list(
        data.get("ai_history", [])
    )

    # Показываем индикатор набора текста
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing",
    )

    try:
        # Заказы этого клиента, чтобы AI мог ответить «где мой заказ?».
        # Если не получилось загрузить — AI ответит без них.
        try:
            orders_context = await get_orders_context(
                message.from_user.id
            )
        except Exception:
            logger.exception("Не удалось загрузить заказы для AI")
            orders_context = None

        # Запрос к Gemini с памятью диалога
        answer, success = await ask_ai(
            question=message.text,
            history=history,
            client_context=orders_context,
        )

        # Сохраняем только успешные ответы
        if success:

            history.append({
                "role": "user",
                "text": message.text[:1000],
            })

            history.append({
                "role": "model",
                "text": answer[:1000],
            })

            # Ограничиваем размер истории
            history = history[-MAX_HISTORY_MESSAGES:]

            await state.update_data(
                ai_history=history,
            )

        # Отправляем ответ клиенту
        await message.answer(
            html.escape(answer[:4000])
        )

    except Exception:
        logger.exception(
            "Ошибка AI-помощника Nurlight"
        )

        await message.answer(
            "⚠️ Произошла ошибка AI.\n"
            "Пожалуйста, попробуйте позже."
        )