from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Текст кнопок
CANCEL_BUTTON = "⬅️ Отменить"
SEND_PHONE_BUTTON = "📱 Отправить номер"
NO_COMMENT_BUTTON = "Без комментария"


# Данные нажатий inline-кнопок
class OrderCallback(CallbackData, prefix="order"):
    action: str


# Кнопка отмены оформления
cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=CANCEL_BUTTON)]
    ],
    resize_keyboard=True
)


# Кнопки для ввода телефона
phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text=SEND_PHONE_BUTTON,
                request_contact=True
            )
        ],
        [KeyboardButton(text=CANCEL_BUTTON)]
    ],
    resize_keyboard=True
)


# Кнопки для комментария
comment_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=NO_COMMENT_BUTTON)],
        [KeyboardButton(text=CANCEL_BUTTON)]
    ],
    resize_keyboard=True
)


# Подтверждение заказа
def confirm_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Подтвердить",
        callback_data=OrderCallback(action="confirm")
    )
    builder.button(
        text="✏️ Изменить",
        callback_data=OrderCallback(action="edit")
    )
    builder.button(
        text="❌ Отмена",
        callback_data=OrderCallback(action="cancel")
    )

    builder.adjust(1, 2)
    return builder.as_markup()


# Выбор поля для редактирования
def edit_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="📍 Адрес",
        callback_data=OrderCallback(action="edit_address")
    )
    builder.button(
        text="📱 Телефон",
        callback_data=OrderCallback(action="edit_phone")
    )
    builder.button(
        text="💬 Комментарий",
        callback_data=OrderCallback(action="edit_comment")
    )
    builder.button(
        text="⬅️ Назад",
        callback_data=OrderCallback(action="back")
    )

    builder.adjust(3, 1)
    return builder.as_markup()


# Повторная попытка при ошибке
def retry_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🔁 Повторить",
        callback_data=OrderCallback(action="retry")
    )
    builder.button(
        text="❌ Отмена",
        callback_data=OrderCallback(action="cancel")
    )

    builder.adjust(2)
    return builder.as_markup()