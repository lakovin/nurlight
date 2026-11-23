import asyncio
import html
import logging

from aiogram import BaseMiddleware, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from bot.i18n import localized, t
from bot.keyboards.cart import CartCallback
from bot.keyboards.main_menu import ALL_MENU_BUTTONS, main_menu
from bot.keyboards.order import (
    CANCEL_BUTTONS,
    KEEP_PHONE_PREFIXES,
    NO_COMMENT_BUTTONS,
    SKIP_BUTTONS,
    OrderCallback,
    address_note_keyboard,
    cancel_keyboard,
    comment_keyboard,
    confirm_keyboard,
    edit_keyboard,
    location_keyboard,
    phone_keyboard,
    retry_keyboard,
    saved_phone_keyboard,
)
from bot.services.clients import get_or_register_client
from bot.services.delivery import delivery_fee_for, delivery_text
from bot.services.payment import (
    available as payment_available,
    send_order_invoice,
)
from bot.services.my_orders import client_order_number
from bot.services.orders import (
    create_order,
    get_client_phone,
    reconcile_cart,
    save_client_phone,
)
from bot.services.validation import (
    format_money,
    format_phone,
    normalize_phone,
    validate_address_note,
    validate_comment,
)
from bot.states import OrderForm


router = Router()
logger = logging.getLogger(__name__)

# Защита от одновременных подтверждений в одном процессе бота
_order_locks: dict[int, asyncio.Lock] = {}


# ---------- Вспомогательные функции ----------

async def reset_checkout(state: FSMContext) -> None:
    """Сбрасывает оформление, сохраняя корзину."""
    cart = (await state.get_data()).get("cart", {})

    await state.clear()

    if cart:
        await state.update_data(cart=cart)


# Кнопки главного меню (на всех языках): нажатие во время оформления прерывает его
MENU_BUTTONS = ALL_MENU_BUTTONS


class CheckoutInterruptMiddleware(BaseMiddleware):
    """Команда или кнопка меню во время оформления прерывает его.

    Корзина сохраняется, а сообщение идёт дальше к обычному обработчику,
    поэтому /start, /cart или «🛍 Каталог» не попадают в адрес или комментарий.
    """

    async def __call__(self, handler, event: Message, data: dict):
        text = event.text or ""
        state = data.get("state")

        if (
            state is not None
            and data.get("raw_state") in OrderForm.__all_states_names__
            and (text.startswith("/") or text in MENU_BUTTONS)
        ):
            await reset_checkout(state)

            # Дальше сообщение обрабатывается как вне оформления
            data["raw_state"] = None

            await event.answer(
                t("checkout_interrupted"),
                reply_markup=main_menu(),
            )

        return await handler(event, data)


router.message.outer_middleware(CheckoutInterruptMiddleware())


async def show_order_summary(
    message: Message,
    state: FSMContext
) -> None:
    """Показывает итоговую информацию заказа."""

    data = await state.get_data()

    cart, items, removed = await reconcile_cart(
        data.get("cart", {})
    )

    await state.update_data(cart=cart, editing=False)

    if removed:
        removed_names = "\n".join(
            f"• {html.escape(name)}"
            for name in removed
        )

        await message.answer(
            t("items_became_unavailable")
            + removed_names
        )

    if not items:
        await reset_checkout(state)

        await message.answer(
            t("cart_empty_to_catalog"),
            reply_markup=main_menu(),
        )
        return

    # Убираем кнопки ввода телефона и комментария
    await message.answer(
        t("order_data"),
        reply_markup=ReplyKeyboardRemove(),
    )

    lines = [t("review_title"), ""]
    total = 0

    for product, quantity in items:
        subtotal = product.price * quantity
        total += subtotal

        lines.append(
            f"• {html.escape(localized(product, 'name'))} × {quantity} — "
            f"{format_money(subtotal)}"
        )

    # Доставка входит в сумму заказа: 500 ₸, бесплатно от порога
    fee = delivery_fee_for(total)

    lines.extend([
        "",
        t("label_items", amount=format_money(total)),
        f"🚚 {delivery_text(fee)}",
        t("label_total", amount=format_money(total + fee)),
        t(
            "summary_location",
            url=(
                "https://www.google.com/maps?q="
                f"{data['latitude']},{data['longitude']}"
            ),
        ),
        t(
            "summary_note",
            text=html.escape(data.get("address") or t("word_none_low")),
        ),
        t("summary_phone", text=html.escape(format_phone(data["phone"]))),
        t(
            "summary_comment",
            text=html.escape(data.get("comment") or t("word_none_cap")),
        ),
        "",
        t("confirm_question"),
    ])

    await state.set_state(OrderForm.confirm)

    await message.answer(
        "\n".join(lines),
        reply_markup=confirm_keyboard(),
    )


async def after_phone_received(
    message: Message,
    state: FSMContext
) -> None:
    """Определяет следующий шаг после ввода телефона."""

    data = await state.get_data()

    if data.get("editing"):
        await show_order_summary(message, state)
        return

    await state.set_state(OrderForm.comment)

    await message.answer(
        t("step_comment"),
        reply_markup=comment_keyboard(),
    )


# ---------- Начало оформления ----------

@router.callback_query(
    CartCallback.filter(F.action == "checkout")
)
async def start_checkout(
    callback: CallbackQuery,
    state: FSMContext
) -> None:

    # Профиль клиента нужен до шага телефона: туда сохраняется номер
    await get_or_register_client(
        callback.from_user.id,
        callback.from_user.full_name,
    )

    data = await state.get_data()

    cart, items, removed = await reconcile_cart(
        data.get("cart", {})
    )

    await state.update_data(cart=cart)
    await callback.answer()

    if removed:
        removed_names = "\n".join(
            f"• {html.escape(name)}"
            for name in removed
        )

        await callback.message.answer(
            t("items_removed_from_cart")
            + removed_names
        )

    if not items:
        await callback.message.answer(t("cart_empty_choose"))
        return

    await state.update_data(editing=False)
    await state.set_state(OrderForm.location)

    await callback.message.answer(
        t("step_location"),
        reply_markup=location_keyboard(),
    )


# ---------- Отмена оформления ----------

@router.message(
    StateFilter(OrderForm),
    F.text.in_(CANCEL_BUTTONS)
)
async def cancel_checkout(
    message: Message,
    state: FSMContext
) -> None:

    await reset_checkout(state)

    await message.answer(
        t("checkout_cancelled"),
        reply_markup=main_menu(),
    )


@router.callback_query(
    StateFilter(OrderForm),
    OrderCallback.filter(F.action == "cancel")
)
async def cancel_order(
    callback: CallbackQuery,
    state: FSMContext
) -> None:

    await reset_checkout(state)

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        t("checkout_cancelled"),
        reply_markup=main_menu(),
    )

    await callback.answer()


# ---------- Шаг 1. Геолокация ----------

@router.message(OrderForm.location, F.location)
async def receive_location(
    message: Message,
    state: FSMContext
) -> None:

    await state.update_data(
        latitude=message.location.latitude,
        longitude=message.location.longitude,
    )

    data = await state.get_data()

    if data.get("editing"):
        await show_order_summary(message, state)
        return

    await state.set_state(OrderForm.address)

    await message.answer(
        t("step_note"),
        reply_markup=address_note_keyboard(),
    )


@router.message(OrderForm.location)
async def invalid_location(message: Message) -> None:
    await message.answer(t("need_location"))


# ---------- Шаг 2. Уточнение адреса (по желанию) ----------

@router.message(OrderForm.address, F.text)
async def receive_address(
    message: Message,
    state: FSMContext
) -> None:

    address = message.text.strip()

    if address in SKIP_BUTTONS:
        address = ""
    else:
        error = validate_address_note(address)

        if error:
            await message.answer(error)
            return

    await state.update_data(address=address)

    data = await state.get_data()

    if data.get("editing"):
        await show_order_summary(message, state)
        return

    await state.set_state(OrderForm.phone)

    # Телефон уже есть в профиле — предлагаем оставить его или указать другой
    saved_phone = await get_client_phone(message.from_user.id)

    if saved_phone:
        label = format_phone(saved_phone)

        await state.update_data(saved_phone=saved_phone)

        await message.answer(
            t("step_phone_saved", phone=html.escape(label)),
            reply_markup=saved_phone_keyboard(label),
        )
        return

    await message.answer(
        t("step_phone"),
        reply_markup=phone_keyboard(),
    )


@router.message(OrderForm.address)
async def invalid_address(message: Message) -> None:
    await message.answer(t("need_note_text"))


# ---------- Шаг 3. Телефон ----------

@router.message(OrderForm.phone, F.contact)
async def receive_contact(
    message: Message,
    state: FSMContext
) -> None:

    if message.contact.user_id != message.from_user.id:
        await message.answer(t("need_own_phone"))
        return

    phone = normalize_phone(
        message.contact.phone_number
    )

    if phone is None:
        await message.answer(t("bad_phone_format"))
        return

    await save_client_phone(
        message.from_user.id,
        phone
    )

    await state.update_data(phone=phone)

    await after_phone_received(message, state)


@router.message(
    OrderForm.phone,
    F.text.startswith(KEEP_PHONE_PREFIXES)
)
async def keep_saved_phone(
    message: Message,
    state: FSMContext
) -> None:

    data = await state.get_data()
    phone = data.get("saved_phone")

    if not phone:
        await message.answer(t("phone_enter_or_contact"))
        return

    await state.update_data(phone=phone)

    await after_phone_received(message, state)


@router.message(OrderForm.phone, F.text)
async def receive_phone(
    message: Message,
    state: FSMContext
) -> None:

    phone = normalize_phone(message.text)

    if phone is None:
        await message.answer(t("bad_phone_example"))
        return

    # Сохраняем в профиль в любом случае (решение №2 в сценариях)
    await save_client_phone(
        message.from_user.id,
        phone
    )

    await state.update_data(phone=phone)

    await after_phone_received(message, state)


@router.message(OrderForm.phone)
async def invalid_phone(message: Message) -> None:
    await message.answer(t("phone_use_button"))


# ---------- Шаг 4. Комментарий ----------

@router.message(
    OrderForm.comment,
    F.text.in_(NO_COMMENT_BUTTONS)
)
async def skip_comment(
    message: Message,
    state: FSMContext
) -> None:

    await state.update_data(comment="")
    await show_order_summary(message, state)


@router.message(OrderForm.comment, F.text)
async def receive_comment(
    message: Message,
    state: FSMContext
) -> None:

    comment = message.text.strip()
    error = validate_comment(comment)

    if error:
        await message.answer(error)
        return

    await state.update_data(comment=comment)
    await show_order_summary(message, state)


@router.message(OrderForm.comment)
async def invalid_comment(message: Message) -> None:
    await message.answer(t("need_comment"))


# ---------- Меню редактирования ----------

@router.callback_query(
    OrderForm.confirm,
    OrderCallback.filter(F.action == "edit")
)
async def edit_order(callback: CallbackQuery) -> None:

    await callback.message.edit_text(
        t("edit_title"),
        reply_markup=edit_keyboard(),
    )

    await callback.answer()


# ---------- Изменить геолокацию ----------

@router.callback_query(
    OrderForm.confirm,
    OrderCallback.filter(F.action == "edit_location")
)
async def edit_location(
    callback: CallbackQuery,
    state: FSMContext
) -> None:

    await state.update_data(editing=True)
    await state.set_state(OrderForm.location)

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        t("edit_location_prompt"),
        reply_markup=location_keyboard(),
    )

    await callback.answer()


# ---------- Изменить уточнение адреса ----------

@router.callback_query(
    OrderForm.confirm,
    OrderCallback.filter(F.action == "edit_address")
)
async def edit_address(
    callback: CallbackQuery,
    state: FSMContext
) -> None:

    await state.update_data(editing=True)
    await state.set_state(OrderForm.address)

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        t("edit_note_prompt"),
        reply_markup=address_note_keyboard(),
    )

    await callback.answer()


# ---------- Изменить телефон ----------

@router.callback_query(
    OrderForm.confirm,
    OrderCallback.filter(F.action == "edit_phone")
)
async def edit_phone(
    callback: CallbackQuery,
    state: FSMContext
) -> None:

    await state.update_data(editing=True)
    await state.set_state(OrderForm.phone)

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        t("edit_phone_prompt"),
        reply_markup=phone_keyboard(),
    )

    await callback.answer()


# ---------- Изменить комментарий ----------

@router.callback_query(
    OrderForm.confirm,
    OrderCallback.filter(F.action == "edit_comment")
)
async def edit_comment(
    callback: CallbackQuery,
    state: FSMContext
) -> None:

    await state.update_data(editing=True)
    await state.set_state(OrderForm.comment)

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        t("edit_comment_prompt"),
        reply_markup=comment_keyboard(),
    )

    await callback.answer()


# ---------- Назад к заказу ----------

@router.callback_query(
    OrderForm.confirm,
    OrderCallback.filter(F.action == "back")
)
async def back_to_summary(
    callback: CallbackQuery,
    state: FSMContext
) -> None:

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.answer()

    await show_order_summary(
        callback.message,
        state
    )


@router.message(OrderForm.confirm)
async def invalid_confirm_input(message: Message) -> None:
    await message.answer(t("use_buttons"))


# ---------- Шаг 5. Сохранение заказа ----------

@router.callback_query(
    OrderForm.confirm,
    OrderCallback.filter(
        F.action.in_({"confirm", "retry"})
    ),
)
async def confirm_order(
    callback: CallbackQuery,
    state: FSMContext
) -> None:

    user_id = callback.from_user.id
    lock = _order_locks.setdefault(
        user_id,
        asyncio.Lock()
    )

    async with lock:

        if await state.get_state() != OrderForm.confirm.state:
            await callback.answer(t("order_in_progress"))
            return

        data = await state.get_data()

        await state.set_state(None)
        await callback.answer()

        try:
            cart, items, removed = await reconcile_cart(
                data.get("cart", {})
            )

            await state.update_data(cart=cart)

            if removed or not items:

                if items:
                    await callback.message.answer(t("cart_changed"))

                    await show_order_summary(
                        callback.message,
                        state
                    )
                else:
                    await reset_checkout(state)

                    await callback.message.answer(
                        t("items_gone"),
                        reply_markup=main_menu(),
                    )

                return

            comment = data.get("comment", "")

            order = await create_order(
                telegram_id=user_id,
                name=callback.from_user.full_name,
                cart=cart,
                address=data.get("address", ""),
                comment=comment,
                latitude=data["latitude"],
                longitude=data["longitude"],
            )

        except Exception:
            logger.exception(
                "Ошибка при создании заказа"
            )

            await state.set_state(OrderForm.confirm)

            await callback.message.answer(
                t("order_create_failed"),
                reply_markup=retry_keyboard(),
            )

            return

        await state.clear()

        # Клиент видит номер среди своих заказов, а не общий номер заказа
        client_number = await client_order_number(order.pk)

        try:
            await callback.message.edit_reply_markup(
                reply_markup=None
            )

            await callback.message.answer(
                t("order_created", number=client_number),
                reply_markup=main_menu(),
            )

        except Exception:
            logger.exception(
                "Заказ сохранён, но не удалось "
                "отправить подтверждение"
            )

        # Счёт за товары. Если не получилось — заказ всё равно создан,
        # оплатить можно позже в «Моих заказах»
        try:
            if await send_order_invoice(
                callback.message,
                order.pk,
                client_number,
                order.total - order.delivery_fee,
                order.delivery_fee,
            ):
                await callback.message.answer(t("pay_hint"))
            elif not payment_available():
                # Заглушка: оплата в боте ещё не подключена
                await callback.message.answer(t("pay_soon"))
        except Exception:
            logger.exception(
                "Заказ %s создан, но счёт не выставлен", order.pk
            )


# ---------- Старые кнопки ----------

@router.callback_query(OrderCallback.filter())
async def old_order_button(callback: CallbackQuery) -> None:
    await callback.answer(
        t("old_button"),
        show_alert=True,
    )