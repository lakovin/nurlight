from asgiref.sync import sync_to_async
from delivery import payments
from delivery.models import Order

from bot.services.my_orders import (
    cancel_by_client,
    get_last_orders,
    get_order_for_client,
    get_orders_context,
)
from bot.services.payment import can_invoice, demo_enabled, demo_pay
from bot.tests.helpers import OTHER_TG_ID, TG_ID, BotTestCase


class OrderCardTests(BotTestCase):
    async def test_card_has_delivery_and_total(self):
        order = await self.make_order(self.pizza)
        card = await get_order_for_client(TG_ID, order.pk)
        self.assertEqual(card["items_total"], 2900)
        self.assertEqual(card["delivery_fee"], 500)
        self.assertEqual(card["total"], 3400)
        self.assertEqual(len(card["items"]), 1)

    async def test_foreign_order_is_hidden(self):
        order = await self.make_order(self.pizza)
        await self.make_client(OTHER_TG_ID)
        self.assertIsNone(await get_order_for_client(OTHER_TG_ID, order.pk))

    async def test_list_is_limited_and_own_only(self):
        for _ in range(12):
            await self.make_order(self.pizza)
        await self.make_order(self.pizza, telegram_id=OTHER_TG_ID)
        orders = await get_last_orders(TG_ID)
        self.assertEqual(len(orders), 10)
        self.assertEqual([o["id"] for o in orders], sorted((o["id"] for o in orders), reverse=True))

    async def test_ai_context_has_no_address_or_phone(self):
        await self.make_client(TG_ID, phone="+77009998877")
        order = await self.make_order(self.pizza)
        await Order.objects.filter(pk=order.pk).aupdate(address="СЕКРЕТНЫЙ АДРЕС")
        context = await get_orders_context(TG_ID)
        self.assertIn(order.number, context)
        self.assertNotIn("СЕКРЕТНЫЙ", context)
        self.assertNotIn("9998877", context)


class CancelTests(BotTestCase):
    async def test_new_unpaid_order_is_cancelled(self):
        order = await self.make_order()
        self.assertEqual(await cancel_by_client(TG_ID, order.pk), "cancelled")
        self.assertEqual((await Order.objects.aget(pk=order.pk)).status, Order.Status.CANCELLED)

    async def test_second_cancel_does_nothing(self):
        order = await self.make_order()
        await cancel_by_client(TG_ID, order.pk)
        self.assertEqual(await cancel_by_client(TG_ID, order.pk), "already_cancelled")

    async def test_accepted_order_cannot_be_cancelled(self):
        order = await self.make_order(status=Order.Status.ACCEPTED)
        self.assertEqual(await cancel_by_client(TG_ID, order.pk), "too_late")
        self.assertEqual((await Order.objects.aget(pk=order.pk)).status, Order.Status.ACCEPTED)

    async def test_paid_order_cannot_be_cancelled(self):
        order = await self.make_order()
        await Order.objects.filter(pk=order.pk).aupdate(payment_status=Order.PaymentStatus.PAID)
        self.assertEqual(await cancel_by_client(TG_ID, order.pk), "paid")
        self.assertEqual((await Order.objects.aget(pk=order.pk)).status, Order.Status.NEW)

    async def test_foreign_order_cannot_be_cancelled(self):
        order = await self.make_order()
        await self.make_client(OTHER_TG_ID)
        self.assertEqual(await cancel_by_client(OTHER_TG_ID, order.pk), "not_found")
        self.assertEqual((await Order.objects.aget(pk=order.pk)).status, Order.Status.NEW)


class PaymentTests(BotTestCase):
    def test_demo_mode_is_on_for_tests(self):
        self.assertTrue(demo_enabled())

    def test_minimum_invoice(self):
        from decimal import Decimal

        self.assertFalse(can_invoice(Decimal("517")))
        self.assertTrue(can_invoice(Decimal("518")))

    async def test_demo_payment_marks_order_paid_once(self):
        order = await self.make_order()
        self.assertIsNone(await demo_pay(TG_ID, order.pk))

        saved = await Order.objects.aget(pk=order.pk)
        self.assertEqual(saved.payment_status, Order.PaymentStatus.PAID)
        self.assertTrue(saved.telegram_charge_id.startswith("demo-"))
        first_charge = saved.telegram_charge_id

        self.assertIsNotNone(await demo_pay(TG_ID, order.pk))  # повторно нельзя
        self.assertEqual((await Order.objects.aget(pk=order.pk)).telegram_charge_id, first_charge)

    async def test_foreign_user_cannot_pay_for_order(self):
        order = await self.make_order()
        await self.make_client(OTHER_TG_ID)
        self.assertIsNotNone(await demo_pay(OTHER_TG_ID, order.pk))
        self.assertEqual((await Order.objects.aget(pk=order.pk)).payment_status, Order.PaymentStatus.UNPAID)

    async def test_cancelled_order_cannot_be_paid(self):
        order = await self.make_order(status=Order.Status.CANCELLED)
        self.assertIsNotNone(await demo_pay(TG_ID, order.pk))

    async def test_check_before_payment_validates_amount(self):
        order = await self.make_order()
        check = sync_to_async(payments.check_before_payment)
        good = payments.amount(order.total)

        self.assertIsNone(await check(f"order:{order.pk}", TG_ID, good, "KZT"))
        self.assertIsNotNone(await check(f"order:{order.pk}", TG_ID, good - 1, "KZT"))
        self.assertIsNotNone(await check(f"order:{order.pk}", TG_ID, good, "USD"))
        self.assertIsNotNone(await check(f"order:{order.pk}", OTHER_TG_ID, good, "KZT"))
        self.assertIsNotNone(await check("order:999999", TG_ID, good, "KZT"))
        self.assertIsNotNone(await check("hack", TG_ID, good, "KZT"))
