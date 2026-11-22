import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from asgiref.sync import sync_to_async

from bot.keyboards.payment import DemoPayCallback
from bot.services.payment import demo_enabled, demo_pay
from delivery import payments

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(DemoPayCallback.filter())
async def demo_pay_handler(
    callback: CallbackQuery,
    callback_data: DemoPayCallback,
):
    """Демо-оплата: отмечает заказ оплаченным без списания денег."""

    if not demo_enabled():
        await callback.answer("Тестовая оплата выключена.", show_alert=True)
        return

    try:
        error = await demo_pay(
            callback.from_user.id,
            callback_data.kind,
            callback_data.order_id,
        )
    except Exception:
        logger.exception("Ошибка демо-оплаты")
        error = "Не удалось выполнить оплату. Попробуйте позже."

    if error:
        await callback.answer(error, show_alert=True)
        return

    await callback.message.edit_text(
        "✅ Тестовая оплата прошла.\n"
        "Деньги не списывались, заказ отмечен оплаченным.",
    )
    await callback.answer()


@router.pre_checkout_query()
async def before_payment(query: PreCheckoutQuery):
    """Telegram спрашивает, можно ли списывать деньги (ответ — до 10 секунд)."""

    try:
        error = await sync_to_async(payments.check_before_payment)(
            query.invoice_payload,
            query.from_user.id,
            query.total_amount,
            query.currency,
        )
    except Exception:
        logger.exception("Ошибка проверки перед оплатой")
        error = "Не удалось проверить заказ. Попробуйте ещё раз позже."

    await query.answer(ok=error is None, error_message=error)


@router.message(F.successful_payment)
async def payment_done(message: Message):
    """Деньги списаны: отмечаем оплату в базе."""

    payment = message.successful_payment
    is_delivery = payment.invoice_payload.startswith(f"{payments.DELIVERY}:")

    try:
        marked = await sync_to_async(payments.mark_paid)(
            payment.invoice_payload,
            message.from_user.id,
            payment.total_amount,
            payment.currency,
            payment.telegram_payment_charge_id,
            payment.provider_payment_charge_id,
        )
    except Exception:
        # Деньги уже списаны: номера платежа сохраняем в лог для разбора
        logger.exception(
            "Платёж получен, но не записан в базу: %s / %s",
            payment.telegram_payment_charge_id,
            payment.provider_payment_charge_id,
        )

        await message.answer(
            "✅ Платёж получен. Не удалось сразу отметить его в системе, "
            "оператор проверит оплату вручную."
        )
        return

    if not marked:
        # Уже было отмечено или заказ не найден — деньги списаны, пусть проверят
        logger.warning(
            "Платёж %s не отмечен (повтор или чужой заказ)",
            payment.telegram_payment_charge_id,
        )

    await message.answer(
        "✅ Доставка оплачена, спасибо!"
        if is_delivery
        else "✅ Оплата прошла, спасибо! Заказ передан оператору."
    )
