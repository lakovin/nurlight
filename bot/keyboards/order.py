from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import t, variants

# Тексты кнопок на всех языках: по ним обработчики узнают нажатие,
# какой бы язык ни выбрал клиент
CANCEL_BUTTONS = variants("btn_cancel")
NO_COMMENT_BUTTONS = variants("btn_no_comment")
SKIP_BUTTONS = variants("btn_skip")
KEEP_PHONE_PREFIXES = tuple(variants("btn_keep_prefix"))


# Данные нажатий inline-кнопок
class OrderCallback(CallbackData, prefix="order"):
    action: str


# Кнопка отмены оформления
def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_cancel"))]
        ],
        resize_keyboard=True
    )


# Кнопки для ввода телефона
def phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=t("btn_send_phone"),
                    request_contact=True
                )
            ],
            [KeyboardButton(text=t("btn_cancel"))]
        ],
        resize_keyboard=True
    )


# Адрес клиент указывает только геолокацией
def location_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=t("btn_send_location"),
                    request_location=True
                )
            ],
            [KeyboardButton(text=t("btn_cancel"))]
        ],
        resize_keyboard=True
    )


# Необязательное уточнение адреса (подъезд, этаж, квартира)
def address_note_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_skip"))],
            [KeyboardButton(text=t("btn_cancel"))]
        ],
        resize_keyboard=True
    )


# Телефон уже есть в профиле: оставить его, отправить другой или ввести вручную
def saved_phone_keyboard(phone_label: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"{t('btn_keep_prefix')} {phone_label}")],
            [
                KeyboardButton(
                    text=t("btn_send_phone"),
                    request_contact=True
                )
            ],
            [KeyboardButton(text=t("btn_cancel"))]
        ],
        resize_keyboard=True
    )


# Кнопки для комментария
def comment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_no_comment"))],
            [KeyboardButton(text=t("btn_cancel"))]
        ],
        resize_keyboard=True
    )


# Подтверждение заказа
def confirm_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text=t("btn_confirm"),
        callback_data=OrderCallback(action="confirm")
    )
    builder.button(
        text=t("btn_edit"),
        callback_data=OrderCallback(action="edit")
    )
    builder.button(
        text=t("btn_cancel_inline"),
        callback_data=OrderCallback(action="cancel")
    )

    builder.adjust(1, 2)
    return builder.as_markup()


# Выбор поля для редактирования
def edit_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text=t("btn_edit_location"),
        callback_data=OrderCallback(action="edit_location")
    )
    builder.button(
        text=t("btn_edit_note"),
        callback_data=OrderCallback(action="edit_address")
    )
    builder.button(
        text=t("btn_edit_phone"),
        callback_data=OrderCallback(action="edit_phone")
    )
    builder.button(
        text=t("btn_edit_comment"),
        callback_data=OrderCallback(action="edit_comment")
    )
    builder.button(
        text=t("btn_back"),
        callback_data=OrderCallback(action="back")
    )

    builder.adjust(2, 2, 1)
    return builder.as_markup()


# Повторная попытка при ошибке
def retry_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text=t("btn_retry"),
        callback_data=OrderCallback(action="retry")
    )
    builder.button(
        text=t("btn_cancel_inline"),
        callback_data=OrderCallback(action="cancel")
    )

    builder.adjust(2)
    return builder.as_markup()
