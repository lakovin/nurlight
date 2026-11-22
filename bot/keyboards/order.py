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


LOCATION_BUTTON = "📍 Отправить геолокацию"
SKIP_ADDRESS_BUTTON = "Пропустить"

# Адрес клиент указывает только геолокацией
location_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text=LOCATION_BUTTON,
                request_location=True
            )
        ],
        [KeyboardButton(text=CANCEL_BUTTON)]
    ],
    resize_keyboard=True
)

# Необязательное уточнение адреса (подъезд, этаж, квартира)
address_note_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=SKIP_ADDRESS_BUTTON)],
        [KeyboardButton(text=CANCEL_BUTTON)]
    ],
    resize_keyboard=True
)

KEEP_PHONE_PREFIX = "✅ Оставить"


# Телефон уже есть в профиле: оставить его, отправить другой или ввести вручную
def saved_phone_keyboard(phone_label: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"{KEEP_PHONE_PREFIX} {phone_label}")],
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
        text="📍 Геолокация",
        callback_data=OrderCallback(action="edit_location")
    )
    builder.button(
        text="🏠 Уточнение адреса",
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

    builder.adjust(2, 2, 1)
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