import html

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.faq import get_faq_questions, get_faq_answer

router = Router()

FAQ_BUTTON = "❓ Частые вопросы"


class FAQCallback(CallbackData, prefix="faq"):
    action: str
    faq_id: int = 0
    language: str = "ru"


def language_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🇷🇺 Русский",
        callback_data=FAQCallback(
            action="language", language="ru"
        ),
    )
    builder.button(
        text="🇰🇿 Қазақша",
        callback_data=FAQCallback(
            action="language", language="kk"
        ),
    )

    builder.adjust(1)
    return builder.as_markup()


def faq_keyboard(questions: list[dict], language: str):
    builder = InlineKeyboardBuilder()

    for item in questions:
        builder.button(
            text=item["question"][:60],
            callback_data=FAQCallback(
                action="answer",
                faq_id=item["id"],
                language=language,
            ),
        )

    builder.button(
        text="⬅️ Тілді өзгерту" if language == "kk"
        else "⬅️ Сменить язык",
        callback_data=FAQCallback(action="choose"),
    )

    builder.adjust(1)
    return builder.as_markup()


def back_keyboard(language: str):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="⬅️ Сұрақтарға оралу" if language == "kk"
        else "⬅️ Назад к вопросам",
        callback_data=FAQCallback(
            action="back", language=language
        ),
    )

    return builder.as_markup()


async def display_questions(callback: CallbackQuery, language: str):
    questions = await get_faq_questions(language=language)

    if language == "kk":
        title = (
            "❓ <b>Nurlight жиі қойылатын сұрақтар</b>\n\n"
            "Қажетті сұрақты таңдаңыз:"
        )
        empty = "❓ Әзірге сұрақтар жоқ."
    else:
        title = (
            "❓ <b>Частые вопросы Nurlight</b>\n\n"
            "Выберите интересующий вопрос:"
        )
        empty = "❓ Пока нет доступных вопросов."

    await callback.message.edit_text(
        title if questions else empty,
        reply_markup=faq_keyboard(questions, language)
        if questions else language_keyboard(),
    )


@router.message(Command("faq"))
@router.message(F.text == FAQ_BUTTON)
async def show_faq(message: Message):
    await message.answer(
        "❓ <b>Частые вопросы Nurlight</b>\n\n"
        "Выберите язык / Тілді таңдаңыз:",
        reply_markup=language_keyboard(),
    )


@router.callback_query(FAQCallback.filter(F.action == "choose"))
async def choose_language(callback: CallbackQuery):
    await callback.message.edit_text(
        "❓ <b>Частые вопросы Nurlight</b>\n\n"
        "Выберите язык / Тілді таңдаңыз:",
        reply_markup=language_keyboard(),
    )
    await callback.answer()


@router.callback_query(FAQCallback.filter(F.action == "language"))
async def select_language(
    callback: CallbackQuery,
    callback_data: FAQCallback,
):
    if callback_data.language not in ("ru", "kk"):
        await callback.answer("Недоступный язык", show_alert=True)
        return

    await display_questions(callback, callback_data.language)
    await callback.answer()


@router.callback_query(FAQCallback.filter(F.action == "answer"))
async def show_answer(
    callback: CallbackQuery,
    callback_data: FAQCallback,
):
    language = callback_data.language

    if language not in ("ru", "kk"):
        await callback.answer("Недоступный язык", show_alert=True)
        return

    item = await get_faq_answer(
        callback_data.faq_id,
        language=language,
    )

    if item is None:
        await callback.answer(
            "Сұрақ табылмады." if language == "kk"
            else "Вопрос больше не доступен.",
            show_alert=True,
        )
        return

    text = (
        f"❓ <b>{html.escape(item['question'])}</b>\n\n"
        f"💬 {html.escape(item['answer'])}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=back_keyboard(language),
    )
    await callback.answer()


@router.callback_query(FAQCallback.filter(F.action == "back"))
async def back_to_faq(
    callback: CallbackQuery,
    callback_data: FAQCallback,
):
    language = callback_data.language

    if language not in ("ru", "kk"):
        await callback.answer("Недоступный язык", show_alert=True)
        return

    await display_questions(callback, language)
    await callback.answer()