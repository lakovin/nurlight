from delivery.models import Category, Product


async def list_categories() -> list[Category]:
    # Только категории, где есть хотя бы один доступный товар
    return [c async for c in Category.objects.filter(products__is_available=True).distinct()]


async def list_products(category_id: int) -> list[Product]:
    return [p async for p in Product.objects.filter(category_id=category_id, is_available=True)]


async def get_product(product_id: int) -> Product | None:
    return await Product.objects.filter(pk=product_id, is_available=True).afirst()
