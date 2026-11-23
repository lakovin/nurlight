"""Общие помощники для тестов: чистая база и быстрое создание данных."""
import unittest
from decimal import Decimal

from delivery.models import Category, Client, Order, Product

from bot.services.language import _cache as language_cache
from bot.services.orders import create_order

TG_ID = 5001
OTHER_TG_ID = 5002


class BotTestCase(unittest.IsolatedAsyncioTestCase):
    """Перед каждым тестом база пустая, а категория и товары создаются заново."""

    async def asyncSetUp(self):
        await Order.objects.all().adelete()
        await Client.objects.all().adelete()
        await Product.objects.all().adelete()
        await Category.objects.all().adelete()
        language_cache.clear()

        self.category = await Category.objects.acreate(name="Пицца")
        self.pizza = await self.make_product("Маргарита", "2900")
        self.big = await self.make_product("Большая", "5200")
        self.hidden = await self.make_product("Нет в наличии", "1000", available=False)

    async def make_product(self, name, price, available=True):
        return await Product.objects.acreate(
            name=name,
            price=Decimal(price),
            category=self.category,
            is_available=available,
        )

    async def make_client(self, telegram_id=TG_ID, phone="", language="ru"):
        return await Client.objects.acreate(
            telegram_id=telegram_id,
            name=f"Клиент {telegram_id}",
            phone=phone,
            language=language,
        )

    async def make_order(self, product=None, quantity=1, telegram_id=TG_ID, status=None):
        """Заказ через настоящий create_order (доставка считается моделью)."""
        product = product or self.pizza

        if not await Client.objects.filter(telegram_id=telegram_id).aexists():
            await self.make_client(telegram_id)

        order = await create_order(
            telegram_id=telegram_id,
            cart={str(product.pk): quantity},
            address="",
            comment="",
            latitude=43.238949,
            longitude=76.889709,
        )

        if status:
            await Order.objects.filter(pk=order.pk).aupdate(status=status)

        return order
