from django.utils import timezone

from bot.i18n import localized, status_label
from bot.services.validation import format_money
from delivery.models import Order

ORDERS_LIMIT = 10

# Статусы для клиента: слово и эмодзи (сценарий 04, раздел 6)
STATUS_EMOJI = {
    Order.Status.NEW: "🕐",
    Order.Status.ACCEPTED: "✅",
    Order.Status.COOKING: "🍳",
    Order.Status.PACKING: "📦",
    Order.Status.READY: "🍽",
    Order.Status.HANDED_TO_COURIER: "🛵",
    Order.Status.IN_TRANSIT: "🚚",
    Order.Status.DELIVERED: "✅",
    Order.Status.CANCELLED: "❌",
}


def status_text(order: Order) -> str:
    emoji = STATUS_EMOJI.get(order.status, "")
    return f"{emoji} {status_label(order.status)}".strip()


# Номер заказа для клиента: порядковый среди ЕГО заказов (1, 2, 3...).
# Общий номер (Order.number, 000019) виден только в панели: по нему
# клиент не может узнать, сколько всего заказов в сервисе.

async def client_numbers(client_id: int) -> dict[int, str]:
    """{id заказа: номер для клиента} по всем заказам одного клиента."""
    ids = [
        pk
        async for pk in (
            Order.objects
            .filter(client_id=client_id)
            .order_by("id")
            .values_list("pk", flat=True)
        )
    ]
    return {pk: str(index) for index, pk in enumerate(ids, start=1)}


async def client_order_number(order_id: int) -> str:
    """Номер одного заказа среди заказов его клиента."""
    client_id = await (
        Order.objects
        .filter(pk=order_id)
        .values_list("client_id", flat=True)
        .afirst()
    )

    if client_id is None:
        return "?"

    number = await Order.objects.filter(
        client_id=client_id, pk__lte=order_id
    ).acount()

    return str(number)


async def get_last_orders(
    telegram_id: int,
    limit: int = ORDERS_LIMIT,
) -> list[dict]:
    """Последние заказы клиента, новые сверху. Только свои."""

    queryset = (
        Order.objects
        .filter(client__telegram_id=telegram_id)
        .order_by("-created_at", "-id")[:limit]
    )

    orders = [order async for order in queryset]
    numbers = await client_numbers(orders[0].client_id) if orders else {}

    return [
        {
            "id": order.pk,
            "number": numbers.get(order.pk, "?"),
            "status": order.status,
            "status_text": status_text(order),
            "total": order.total,
            "created": timezone.localtime(order.created_at),
        }
        for order in orders
    ]


async def get_order_for_client(
    telegram_id: int,
    order_id: int,
) -> dict | None:
    """Карточка заказа. Возвращает None, если заказ чужой или не найден."""

    order = await (
        Order.objects
        .select_related("client")
        .filter(pk=order_id, client__telegram_id=telegram_id)
        .afirst()
    )

    if order is None:
        return None

    # Цена берётся из OrderItem, а не из каталога
    items = [
        {
            "name": localized(item.product, "name"),
            "quantity": item.quantity,
            "price": item.price,
        }
        async for item in order.items.select_related("product").order_by("id")
    ]

    return {
        "id": order.pk,
        "number": await client_order_number(order.pk),
        "status": order.status,
        "status_text": status_text(order),
        "created": timezone.localtime(order.created_at),
        "items": items,
        "total": order.total,
        "address": order.address,
        "phone": order.client.phone,
        "comment": order.comment,
        # Оплата: товары и доставка оплачиваются отдельными счетами
        "paid": order.payment_status == Order.PaymentStatus.PAID,
        # Доставка входит в сумму заказа (total = блюда + доставка)
        "latitude": order.latitude,
        "longitude": order.longitude,
        "items_total": order.total - order.delivery_fee,
        "delivery_fee": order.delivery_fee,
    }


async def get_orders_context(telegram_id: int, limit: int = 3) -> str:
    """Текст о последних заказах клиента для AI-консультанта.

    Только заказы этого клиента. Адрес и телефон не передаются:
    для ответа «где мой заказ» они не нужны.
    """

    now = timezone.localtime()
    lines = [f"Сейчас: {now:%d.%m.%Y, %H:%M} (время Алматы)."]

    orders = [
        order
        async for order in (
            Order.objects
            .filter(client__telegram_id=telegram_id)
            .order_by("-created_at", "-id")[:limit]
        )
    ]
    numbers = await client_numbers(orders[0].client_id) if orders else {}

    found = False

    for order in orders:
        found = True

        items = ", ".join([
            f"{item.product.name} × {item.quantity}"
            async for item in order.items.select_related("product")
        ])

        created = timezone.localtime(order.created_at)

        lines.append(
            f"№{numbers.get(order.pk, '?')} — статус: {order.get_status_display()} — "
            f"сумма: {format_money(order.total)} — "
            f"создан: {created:%d.%m.%Y, %H:%M} — состав: {items or '—'}"
        )

    if not found:
        lines.append("У клиента пока нет заказов.")

    return "\n".join(lines)


async def cancel_by_client(telegram_id: int, order_id: int) -> str:
    """Отмена одним условным обновлением, без «прочитать → проверить → записать».

    Возвращает: "cancelled", "already_cancelled", "paid", "too_late"
    или "not_found". Оплаченный заказ клиент не отменяет: возврат денег
    решает оператор.
    """

    updated = await Order.objects.filter(
        pk=order_id,
        client__telegram_id=telegram_id,
        status=Order.Status.NEW,
        payment_status=Order.PaymentStatus.UNPAID,
    ).aupdate(
        status=Order.Status.CANCELLED,
        updated_at=timezone.now(),
    )

    if updated:
        return "cancelled"

    # Не обновили: выясняем почему (заказ чужой, уже отменён или уже принят)
    row = await (
        Order.objects
        .filter(pk=order_id, client__telegram_id=telegram_id)
        .values_list("status", "payment_status")
        .afirst()
    )

    if row is None:
        return "not_found"

    status, payment_status = row

    if status == Order.Status.CANCELLED:
        return "already_cancelled"

    if payment_status == Order.PaymentStatus.PAID:
        return "paid"

    return "too_late"
