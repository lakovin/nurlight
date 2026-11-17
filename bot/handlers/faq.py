import html

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.faq import (
    get_faq_questions,
    get_faq_answer,
)

router = Router()

FAQ_BUTTON = "❓ Частые вопросы"


class FAQCallback(CallbackData, prefix="faq"):
    action: str
    faq_id: int = 0


def faq_keyboard(questions: list[dict]):
    """Создаёт кнопки с вопросами."""
    builder = InlineKeyboardBuilder()

    for item in questions:
        builder.button(
            text=item["question"][:60],
            callback_data=FAQCallback(
                action="answer",
                faq_id=item["id"],
            ),
        )

    builder.adjust(1)
    return builder.as_markup()


def back_keyboard():
    """Кнопка возврата к списку вопросов."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text="⬅️ Назад к вопросам",
        callback_data=FAQCallback(action="back"),
    )

    return builder.as_markup()


@router.message(Command("faq"))
@router.message(F.text == FAQ_BUTTON)
async def show_faq(message: Message):
    """Показывает список часто задаваемых вопросов."""

    questions = await get_faq_questions()

    if not questions:
        await message.answer(
            "❓ Пока нет доступных вопросов."
        )
        return

    await message.answer(
        "❓ <b>Частые вопросы Nurlight</b>\n\n"
        "Выберите интересующий вопрос:",
        reply_markup=faq_keyboard(questions),
    )


@router.callback_query(
    FAQCallback.filter(F.action == "answer")
)
async def show_answer(
    callback: CallbackQuery,
    callback_data: FAQCallback,
):
    """Показывает ответ из базы Django."""

    item = await get_faq_answer(callback_data.faq_id)

    if item is None:
        await callback.answer(
            "Вопрос больше не доступен.",
            show_alert=True,
        )
        return

    text = (
        f"❓ <b>{html.escape(item['question'])}</b>\n\n"
        f"💬 {html.escape(item['answer'])}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=back_keyboard(),
    )

    await callback.answer()


@router.callback_query(
    FAQCallback.filter(F.action == "back")
)
async def back_to_faq(callback: CallbackQuery):
    """Возвращает клиента к вопросам."""

    questions = await get_faq_questions()

    if not questions:
        await callback.message.edit_text(
            "❓ Пока нет доступных вопросов."
        )
    else:
        await callback.message.edit_text(
            "❓ <b>Частые вопросы Nurlight</b>\n\n"
            "Выберите интересующий вопрос:",
            reply_markup=faq_keyboard(questions),
        )

    await callback.answer()