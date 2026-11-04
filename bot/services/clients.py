from delivery.models import Client


async def get_or_register_client(telegram_id: int, name: str) -> Client:
    client, _ = await Client.objects.aget_or_create(telegram_id=telegram_id, defaults={"name": name})
    return client
