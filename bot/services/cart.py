from delivery.models import Product


async def get_cart_items(cart: dict) -> list[tuple[Product, int]]:
    """Превращает корзину {id: количество} в список (товар, количество)."""
    ids = [int(pk) for pk in cart]
    products = {p.pk: p async for p in Product.objects.filter(pk__in=ids, is_available=True)}
    return [(products[int(pk)], qty) for pk, qty in cart.items() if int(pk) in products]