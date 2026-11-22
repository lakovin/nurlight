from delivery.models import Category, Product


async def list_categories() -> list[Category]:
    # Категории, где есть хотя бы один товар (в том числе «нет в наличии»)
    return [c async for c in Category.objects.filter(products__isnull=False).distinct()]


async def list_products(category_id: int) -> list[Product]:
    # Недоступные товары тоже показываем (с пометкой «нет в наличии»), но в конце списка
    return [
        p
        async for p in Product.objects.filter(category_id=category_id).order_by("-is_available", "name")
    ]


async def get_product(product_id: int) -> Product | None:
    """Только доступный товар: его можно положить в корзину."""
    return await Product.objects.filter(pk=product_id, is_available=True).afirst()


async def get_product_any(product_id: int) -> Product | None:
    """Товар независимо от наличия — для карточки."""
    return await Product.objects.filter(pk=product_id).afirst()
