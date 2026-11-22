from delivery.models import Client


async def register_client(telegram_id: int, name: str) -> tuple[Client, bool]:
    """Возвращает клиента и признак «создан только что» (нужен для выбора языка)."""
    return await Client.objects.aget_or_create(telegram_id=telegram_id, defaults={"name": name})


async def get_or_register_client(telegram_id: int, name: str) -> Client:
    client, _ = await register_client(telegram_id, name)
    return client
