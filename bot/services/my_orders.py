from django.utils import timezone

from delivery.models import Order

ORDERS_LIMIT = 10

# Статусы для клиента: слово и эмодзи (сценарий 04, раздел 6)
STATUS_EMOJI = {
    Order.Status.NEW: "🕐",
    Order.Status.ACCEPTED: "✅",
    Order.Status.HANDED_TO_COURIER: "🛵",
    Order.Status.IN_TRANSIT: "🚚",
    Order.Status.DELIVERED: "✅",
    Order.Status.CANCELLED: "❌",
}


def status_text(order: Order) -> str:
    emoji = STATUS_EMOJI.get(order.status, "")
    return f"{emoji} {order.get_status_display()}".strip()


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

    return [
        {
            "id": order.pk,
            "number": order.number,
            "status": order.status,
            "status_text": status_text(order),
            "total": order.total,
            "created": timezone.localtime(order.created_at),
        }
        async for order in queryset
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
            "name": item.product.name,
            "quantity": item.quantity,
            "price": item.price,
        }
        async for item in order.items.select_related("product").order_by("id")
    ]

    return {
        "id": order.pk,
        "number": order.number,
        "status": order.status,
        "status_text": status_text(order),
        "created": timezone.localtime(order.created_at),
        "items": items,
        "total": order.total,
        "address": order.address,
        "phone": order.client.phone,
        "comment": order.comment,
    }


async def cancel_by_client(telegram_id: int, order_id: int) -> str:
    """Отмена одним условным обновлением, без «прочитать → проверить → записать».

    Возвращает: "cancelled", "already_cancelled", "too_late" или "not_found".
    """

    updated = await Order.objects.filter(
        pk=order_id,
        client__telegram_id=telegram_id,
        status=Order.Status.NEW,
    ).aupdate(
        status=Order.Status.CANCELLED,
        updated_at=timezone.now(),
    )

    if updated:
        return "cancelled"

    # Не обновили: выясняем почему (заказ чужой, уже отменён или уже принят)
    status = await (
        Order.objects
        .filter(pk=order_id, client__telegram_id=telegram_id)
        .values_list("status", flat=True)
        .afirst()
    )

    if status is None:
        return "not_found"

    if status == Order.Status.CANCELLED:
        return "already_cancelled"

    return "too_late"
