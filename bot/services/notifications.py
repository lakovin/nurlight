"""Уведомления клиенту о смене статуса заказа (issue #4).

Бот раз в POLL_INTERVAL секунд сравнивает статусы активных заказов в базе
с последними известными и пишет клиенту об изменениях. Так работают любые
способы смены статуса: список заказов, действия «Принять/Отменить»
(они делают массовое обновление, и сигналы Django их бы пропустили).

Ограничения этой версии (миграций нет):
- последние известные статусы хранятся в памяти бота; изменения, которые
  произошли, пока бот был выключен, не отправляются;
- заказы без Telegram у клиента (если такие остались) уведомления не получают.
Надёжный вариант с журналом NotificationLog — позже, вместе с панелью.
"""
import asyncio
import logging
from datetime import datetime

from aiogram import Bot
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Q
from django.utils import timezone

from bot.i18n import t
from bot.keyboards.my_orders import MyOrdersCallback
from bot.services.my_orders import client_order_number
from delivery.models import Order

logger = logging.getLogger(__name__)

POLL_INTERVAL = 10  # секунд между проверками базы
MAX_ATTEMPTS = 3  # сколько раз пытаемся отправить одно уведомление

ACTIVE_STATUSES = (
    Order.Status.NEW,
    Order.Status.ACCEPTED,
    Order.Status.COOKING,
    Order.Status.PACKING,
    Order.Status.READY,
    Order.Status.HANDED_TO_COURIER,
    Order.Status.IN_TRANSIT,
)

# Ключ перевода (bot/i18n.py) на каждый статус, кроме «Новый» (о нём клиент знает из бота).
# Тексты на языке клиента берутся из Client.language.
MESSAGES = {
    Order.Status.ACCEPTED: "notify_accepted",
    Order.Status.COOKING: "notify_cooking",
    # «Упаковывается» отдельным сообщением не отправляем, чтобы не засорять чат
    Order.Status.READY: "notify_ready",
    Order.Status.HANDED_TO_COURIER: "notify_handed_to_courier",
    Order.Status.IN_TRANSIT: "notify_in_transit",
    Order.Status.DELIVERED: "notify_delivered",
    Order.Status.CANCELLED: "notify_cancelled",
}

# order_id -> последний известный статус; order_id -> число неудачных попыток
_known: dict[int, str] = {}
_attempts: dict[int, int] = {}


def mark_known(order_id: int, status: str) -> None:
    """Запоминает статус без уведомления.

    Бот вызывает это сам, когда клиент отменил заказ в боте: он уже
    видел подтверждение, второе сообщение не нужно.
    """
    _known[order_id] = str(status)
    _attempts.pop(order_id, None)


def detect_changes(
    known: dict[int, str],
    rows: list[tuple],
    started_at: datetime,
) -> list[tuple[int, int, str, str]]:
    """Находит заказы, о смене статуса которых нужно сообщить.

    rows — (id заказа, статус, telegram_id, дата создания, язык клиента).
    Возвращает [(id заказа, telegram_id, новый статус, язык)]. Заказы, у которых
    сообщения нет (например, возврат в «Новый»), и первое знакомство со
    старыми заказами просто записываются в known.
    """
    changes = []

    for order_id, status, telegram_id, created_at, language in rows:
        status = str(status)
        previous = known.get(order_id)

        if previous is None:
            if created_at < started_at:
                # Заказ был до запуска бота: запоминаем, не уведомляем
                known[order_id] = status
                continue

            # Заказ создан уже при работающем боте: он начинал с «Новый»
            previous = str(Order.Status.NEW)

        if status == previous:
            known[order_id] = status
        elif status in MESSAGES:
            changes.append((order_id, telegram_id, status, language))
        else:
            known[order_id] = status

    return changes


def orders_keyboard(language: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t("btn_orders", language),
        callback_data=MyOrdersCallback(action="list"),
    )
    return builder.as_markup()


async def notify(
    bot: Bot,
    order_id: int,
    telegram_id: int,
    status: str,
    language: str,
) -> bool:
    """Отправляет одно уведомление на языке клиента. True — больше пытаться не нужно."""

    text = t(MESSAGES[status], language, number=await client_order_number(order_id))

    try:
        await bot.send_message(
            telegram_id,
            text,
            reply_markup=orders_keyboard(language),
        )
        return True

    except TelegramForbiddenError:
        # Клиент заблокировал бота: заказ живёт дальше, повторов нет
        logger.warning(
            "Уведомление по заказу %s не доставлено: бот заблокирован",
            order_id,
        )
        return True

    except TelegramRetryAfter as error:
        await asyncio.sleep(min(error.retry_after, 5))
        error_text = "лимит Telegram"

    except TelegramAPIError as error:
        error_text = str(error)

    attempts = _attempts.get(order_id, 0) + 1
    _attempts[order_id] = attempts

    logger.warning(
        "Уведомление по заказу %s не отправлено (попытка %s из %s): %s",
        order_id,
        attempts,
        MAX_ATTEMPTS,
        error_text,
    )

    return attempts >= MAX_ATTEMPTS


async def poll_once(bot: Bot, started_at: datetime) -> None:
    """Одна проверка базы: новые статусы → уведомления."""

    # Заказ, который был активным, мог стать «Доставлен»/«Отменён»:
    # такой заказ уже не активен в базе, поэтому берём его по id
    active_known = [
        order_id
        for order_id, status in _known.items()
        if status in ACTIVE_STATUSES
    ]

    rows = [
        row
        async for row in (
            Order.objects
            .filter(client__telegram_id__isnull=False)
            .filter(Q(status__in=ACTIVE_STATUSES) | Q(pk__in=active_known))
            .values_list(
                "id", "status", "client__telegram_id", "created_at",
                "client__language",
            )
        )
    ]

    for order_id, telegram_id, status, language in detect_changes(
        _known, rows, started_at
    ):
        if await notify(bot, order_id, telegram_id, status, language):
            mark_known(order_id, status)


async def run(bot: Bot) -> None:
    """Фоновая задача: работает, пока запущен бот."""

    started_at = timezone.now()
    logger.info("Уведомления о статусах заказов включены")

    while True:
        try:
            await poll_once(bot, started_at)
        except asyncio.CancelledError:
            raise
        except Exception:
            # База (например, Neon после сна) или сеть недоступны — повторим
            logger.exception("Ошибка проверки статусов заказов")

        await asyncio.sleep(POLL_INTERVAL)
