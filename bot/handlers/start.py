import html

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import LANG_NAMES, LANGS, current_lang, t
from bot.keyboards.main_menu import LANGUAGE_BUTTONS, main_menu
from bot.services.clients import register_client
from bot.services.language import set_language

router = Router()


class LanguageCallback(CallbackData, prefix="lang"):
    code: str


def language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for code in LANGS:
        builder.button(
            text=LANG_NAMES[code],
            callback_data=LanguageCallback(code=code),
        )

    builder.adjust(1)
    return builder.as_markup()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    client, created = await register_client(user.id, user.full_name)

    if created:
        # Новому клиенту сначала предлагаем выбрать язык
        await message.answer(
            t("lang_choose", "ru"),
            reply_markup=language_keyboard(),
        )
        return

    lang = client.language
    current_lang.set(lang)

    await message.answer(
        t("start_greeting", lang, name=html.escape(client.name)),
        reply_markup=main_menu(lang),
    )


@router.message(Command("language"))
@router.message(F.text.in_(LANGUAGE_BUTTONS))
async def choose_language(message: Message):
    await message.answer(
        t("lang_choose", "ru"),
        reply_markup=language_keyboard(),
    )


@router.callback_query(LanguageCallback.filter())
async def language_chosen(
    callback: CallbackQuery,
    callback_data: LanguageCallback,
    state: FSMContext,
):
    lang = callback_data.code

    if lang not in LANGS:
        await callback.answer()
        return

    await set_language(callback.from_user.id, lang)
    current_lang.set(lang)

    await callback.message.edit_text(t("lang_changed", lang))

    # Выбранный язык применяется сразу: приветствие и меню на нём
    await callback.message.answer(
        t(
            "start_greeting",
            lang,
            name=html.escape(callback.from_user.full_name),
        ),
        reply_markup=main_menu(lang),
    )
    await callback.answer()
