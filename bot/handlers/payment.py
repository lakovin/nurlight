import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from asgiref.sync import sync_to_async

from bot.i18n import t
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
        await callback.answer(t("demo_off"), show_alert=True)
        return

    try:
        error = await demo_pay(
            callback.from_user.id,
            callback_data.order_id,
        )
    except Exception:
        logger.exception("Ошибка демо-оплаты")
        error = t("pay_failed")

    if error:
        await callback.answer(error, show_alert=True)
        return

    await callback.message.edit_text(t("demo_done"))
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
        error = t("precheck_failed")

    await query.answer(ok=error is None, error_message=error)


@router.message(F.successful_payment)
async def payment_done(message: Message):
    """Деньги списаны: отмечаем оплату в базе."""

    payment = message.successful_payment

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

        await message.answer(t("payment_manual"))
        return

    if not marked:
        # Уже было отмечено или заказ не найден — деньги списаны, пусть проверят
        logger.warning(
            "Платёж %s не отмечен (повтор или чужой заказ)",
            payment.telegram_payment_charge_id,
        )

    await message.answer(t("payment_ok"))
