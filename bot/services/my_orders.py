
from django.utils import timezone

from delivery.models import Order


async def get_client_orders(
    telegram_id: int,
    limit: int = 5,
) -> list[dict]:
    """Получает последние заказы конкретного клиента."""

    queryset = (
        Order.objects
        .filter(client__telegram_id=telegram_id)
        .order_by("-created_at", "-id")[:limit]
    )

    orders = []

    async for order in queryset:
        orders.append({
            "id": order.pk,
            "number": order.number,
            "date": timezone.localtime(
                order.created_at
            ).strftime("%d.%m.%Y %H:%M"),
            "status": order.get_status_display(),
            "total": order.total,
        })

    return orders


async def get_client_order(
    telegram_id: int,
    order_id: int,
) -> dict | None:
    """Получает один заказ, проверяя владельца."""

    order = await Order.objects.filter(
        pk=order_id,
        client__telegram_id=telegram_id,
    ).afirst()

    if order is None:
        return None

    return {
        "id": order.pk,
        "number": order.number,
        "date": timezone.localtime(
            order.created_at
        ).strftime("%d.%m.%Y %H:%M"),
        "status": order.get_status_display(),
        "total": order.total,
    }
