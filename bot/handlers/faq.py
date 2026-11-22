import html

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import DEFAULT_LANG, current_lang, t
from bot.keyboards.main_menu import FAQ_BUTTONS
from bot.services.faq import get_faq_answer, get_faq_questions

router = Router()


class FAQCallback(CallbackData, prefix="faq"):
    action: str  # answer, back
    faq_id: int = 0
    language: str = DEFAULT_LANG  # язык, на котором показаны вопросы


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

    builder.adjust(1)
    return builder.as_markup()


def back_keyboard(language: str):
    builder = InlineKeyboardBuilder()

    builder.button(
        text=t("btn_faq_back"),
        callback_data=FAQCallback(action="back", language=language),
    )

    return builder.as_markup()


async def load_questions() -> tuple[list[dict], str]:
    """Вопросы на языке клиента; если их нет (например, на английском) — русские."""
    language = current_lang.get()
    questions = await get_faq_questions(language=language)

    if not questions and language != DEFAULT_LANG:
        language = DEFAULT_LANG
        questions = await get_faq_questions(language=language)

    return questions, language


@router.message(Command("faq"))
@router.message(F.text.in_(FAQ_BUTTONS))
async def show_faq(message: Message):
    questions, language = await load_questions()

    if not questions:
        await message.answer(t("faq_empty"))
        return

    await message.answer(
        t("faq_title"),
        reply_markup=faq_keyboard(questions, language),
    )


@router.callback_query(FAQCallback.filter(F.action == "answer"))
async def show_answer(
    callback: CallbackQuery,
    callback_data: FAQCallback,
):
    item = await get_faq_answer(
        callback_data.faq_id,
        language=callback_data.language,
    )

    if item is None:
        await callback.answer(t("faq_not_found"), show_alert=True)
        return

    text = (
        f"❓ <b>{html.escape(item['question'])}</b>\n\n"
        f"💬 {html.escape(item['answer'])}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=back_keyboard(callback_data.language),
    )
    await callback.answer()


@router.callback_query(FAQCallback.filter(F.action == "back"))
async def back_to_faq(callback: CallbackQuery):
    questions, language = await load_questions()

    if not questions:
        await callback.message.edit_text(t("faq_empty"))
        await callback.answer()
        return

    await callback.message.edit_text(
        t("faq_title"),
        reply_markup=faq_keyboard(questions, language),
    )
    await callback.answer()
