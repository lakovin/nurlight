from asgiref.sync import sync_to_async
from django.db import transaction

from delivery.models import Client, Order, OrderItem, Product


async def reconcile_cart(cart: dict):
    """Проверяет доступность товаров в корзине."""

    ids = [int(product_id) for product_id in cart]

    products = {
        product.pk: product
        async for product in Product.objects.filter(pk__in=ids)
    }

    new_cart = {}
    items = []
    removed = []

    for product_id, quantity in cart.items():
        product = products.get(int(product_id))

        if (
            product is not None
            and product.is_available
            and type(quantity) is int
            and quantity > 0
        ):
            new_cart[str(product_id)] = quantity
            items.append((product, quantity))
        else:
            removed.append(
                product.name if product is not None
                else f"Товар #{product_id}"
            )

    return new_cart, items, removed


async def get_client_phone(telegram_id: int) -> str:
    """Получает сохранённый телефон клиента."""

    client = await Client.objects.filter(
        telegram_id=telegram_id
    ).afirst()

    return client.phone if client else ""


async def save_client_phone(telegram_id: int, phone: str):
    """Сохраняет телефон клиента."""

    await Client.objects.filter(
        telegram_id=telegram_id
    ).aupdate(phone=phone)


@sync_to_async
def create_order(
    telegram_id: int,
    cart: dict,
    address: str,
    comment: str
):
    """Создаёт заказ и его позиции в одной транзакции."""

    if not cart:
        raise ValueError("Корзина пуста")

    with transaction.atomic():

        client = Client.objects.get(
            telegram_id=telegram_id
        )

        products = {
            product.pk: product
            for product in Product.objects.filter(
                pk__in=[int(key) for key in cart],
                is_available=True
            )
        }

        items = []

        for key, quantity in cart.items():
            product = products.get(int(key))

            if product is None:
                raise ValueError("Товар больше недоступен")

            if type(quantity) is not int or quantity <= 0:
                raise ValueError("Неверное количество товара")

            items.append((product, quantity))

        order = Order.objects.create(
            client=client,
            address=address,
            comment=comment
        )

        for product, quantity in items:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

        order.recalculate_total()

        return order