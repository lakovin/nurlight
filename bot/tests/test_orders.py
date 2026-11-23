from decimal import Decimal

from delivery.models import Client, Order

from bot.services.delivery import delivery_fee_for, delivery_text
from bot.services.orders import create_order, reconcile_cart
from bot.services.validation import normalize_phone, validate_address_note, validate_comment
from bot.tests.helpers import TG_ID, BotTestCase


class DeliveryRuleTests(BotTestCase):
    def test_fee_below_threshold(self):
        self.assertEqual(delivery_fee_for(Decimal("4999")), Decimal("500"))

    def test_free_from_threshold(self):
        self.assertEqual(delivery_fee_for(Decimal("5000")), Decimal(0))
        self.assertEqual(delivery_fee_for(Decimal("12000")), Decimal(0))

    def test_text_in_every_language(self):
        from bot.i18n import LANGS, current_lang

        for lang in LANGS:
            current_lang.set(lang)
            self.assertTrue(delivery_text(Decimal(0)))
            self.assertIn("500", delivery_text(Decimal("500")))


class CreateOrderTests(BotTestCase):
    async def test_total_includes_delivery(self):
        order = await self.make_order(self.pizza)  # 2 900 ₸ < 5 000
        self.assertEqual(order.delivery_fee, Decimal("500"))
        self.assertEqual(order.total, Decimal("3400"))

    async def test_free_delivery_from_5000(self):
        order = await self.make_order(self.big)  # 5 200 ₸
        self.assertEqual(order.delivery_fee, Decimal(0))
        self.assertEqual(order.total, Decimal("5200"))

    async def test_price_is_fixed_in_order_item(self):
        order = await self.make_order(self.pizza)
        self.pizza.price = Decimal("9999")
        await self.pizza.asave()
        item = await order.items.afirst()
        self.assertEqual(item.price, Decimal("2900"))

    async def test_location_is_saved(self):
        order = await self.make_order(self.pizza)
        saved = await Order.objects.aget(pk=order.pk)
        self.assertEqual(saved.latitude, Decimal("43.238949"))
        self.assertEqual(saved.longitude, Decimal("76.889709"))

    async def test_client_is_created_when_missing(self):
        self.assertFalse(await Client.objects.filter(telegram_id=777).aexists())
        order = await create_order(
            telegram_id=777,
            cart={str(self.pizza.pk): 1},
            address="",
            comment="",
            name="Новый",
        )
        client = await Client.objects.aget(telegram_id=777)
        self.assertEqual(client.name, "Новый")
        self.assertEqual(order.client_id, client.pk)

    async def test_unavailable_product_is_rejected(self):
        await self.make_client()
        with self.assertRaises(ValueError):
            await create_order(
                telegram_id=TG_ID,
                cart={str(self.hidden.pk): 1},
                address="",
                comment="",
            )

    async def test_empty_cart_is_rejected(self):
        await self.make_client()
        with self.assertRaises(ValueError):
            await create_order(telegram_id=TG_ID, cart={}, address="", comment="")


class ReconcileCartTests(BotTestCase):
    async def test_unavailable_items_are_removed(self):
        cart, items, removed = await reconcile_cart(
            {str(self.pizza.pk): 2, str(self.hidden.pk): 1}
        )
        self.assertEqual(cart, {str(self.pizza.pk): 2})
        self.assertEqual(len(items), 1)
        self.assertEqual(removed, [self.hidden.name])

    async def test_bad_quantity_is_removed(self):
        cart, items, _ = await reconcile_cart({str(self.pizza.pk): 0})
        self.assertEqual(cart, {})
        self.assertEqual(items, [])


class ValidationTests(BotTestCase):
    def test_phone_formats(self):
        self.assertEqual(normalize_phone("8 (700) 111-22-33"), "+77001112233")
        self.assertEqual(normalize_phone("+7 700 111 22 33"), "+77001112233")
        self.assertEqual(normalize_phone("7001112233"), "+77001112233")

    def test_bad_phones(self):
        self.assertIsNone(normalize_phone("12345"))
        self.assertIsNone(normalize_phone("+1 202 555 0100"))
        self.assertIsNone(normalize_phone("abc"))

    def test_comment_and_note_limits(self):
        self.assertIsNone(validate_comment("x" * 500))
        self.assertIsNotNone(validate_comment("x" * 501))
        self.assertIsNone(validate_address_note("Подъезд 2, кв. 5"))
        self.assertIsNotNone(validate_address_note("x" * 501))
