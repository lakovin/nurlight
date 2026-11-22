from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.urls import reverse

from . import payments
from .models import Category, Client, Courier, Order, OrderItem, Product
from .roles import KITCHEN, MANAGER, OPERATOR
from .statistics import collect_statistics


class DeliveryTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client_obj = Client.objects.create(telegram_id=1, name="Айгерим", phone="+77001112233")
        category = Category.objects.create(name="Пицца")
        cls.pizza = Product.objects.create(name="Маргарита", price=Decimal("2900"), category=category)
        cls.courier = Courier.objects.create(name="Ерлан", phone="+77002223344")
        cls.inactive_courier = Courier.objects.create(name="Бывший", phone="+77000000000", is_active=False)

    def make_order(self, status=Order.Status.NEW, quantity=1, courier=None):
        order = Order.objects.create(
            client=self.client_obj, address="Абая 10", status=status, courier=courier
        )
        OrderItem.objects.create(order=order, product=self.pizza, quantity=quantity, price=self.pizza.price)
        order.recalculate_total()
        return order

    def make_staff(self, username, group_name):
        user = User.objects.create_user(username, password="pass", is_staff=True)
        user.groups.add(Group.objects.get(name=group_name))
        return user


class OrderModelTests(DeliveryTestCase):
    def test_recalculate_total_sums_items(self):
        order = self.make_order(quantity=3)
        self.assertEqual(order.total, Decimal("8700"))

    def test_number_is_zero_padded(self):
        order = self.make_order()
        self.assertEqual(order.number, f"{order.pk:06d}")


class RolesTests(DeliveryTestCase):
    def test_groups_created_after_migrate(self):
        self.assertTrue(Group.objects.filter(name=OPERATOR).exists())
        self.assertTrue(Group.objects.filter(name=MANAGER).exists())

    def test_operator_can_change_orders_but_not_products_or_statistics(self):
        operator = self.make_staff("operator", OPERATOR)
        self.assertTrue(operator.has_perm("delivery.change_order"))
        self.assertFalse(operator.has_perm("delivery.delete_order"))
        self.assertFalse(operator.has_perm("delivery.change_product"))
        self.assertFalse(operator.has_perm("delivery.view_statistics"))

    def test_manager_has_everything_in_delivery(self):
        manager = self.make_staff("manager", MANAGER)
        self.assertTrue(manager.has_perm("delivery.change_product"))
        self.assertTrue(manager.has_perm("delivery.delete_order"))
        self.assertTrue(manager.has_perm("delivery.view_statistics"))


class StatisticsPageTests(DeliveryTestCase):
    url = reverse("admin:delivery_order_statistics")

    def test_manager_sees_statistics(self):
        self.make_order(status=Order.Status.DELIVERED, quantity=2, courier=self.courier)
        self.client.force_login(self.make_staff("manager", MANAGER))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Маргарита")
        self.assertContains(response, "Ерлан")

    def test_operator_is_forbidden(self):
        self.client.force_login(self.make_staff("operator", OPERATOR))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_unknown_period_falls_back_to_default(self):
        self.client.force_login(self.make_staff("manager", MANAGER))
        response = self.client.get(self.url, {"period": "abc"})
        self.assertEqual(response.context["period"], "30")

    def test_collect_statistics_numbers(self):
        self.make_order(status=Order.Status.DELIVERED, quantity=2, courier=self.courier)
        self.make_order(status=Order.Status.CANCELLED)
        self.make_order(status=Order.Status.NEW)
        stats = collect_statistics(days=30)
        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["delivered"], 1)
        self.assertEqual(stats["in_progress"], 1)
        self.assertEqual(stats["revenue"], Decimal("5800"))
        self.assertEqual(stats["average_check"], Decimal("5800"))
        self.assertEqual(stats["cancel_rate"], 33)
        # Отменённый заказ не попадает в популярные товары
        self.assertEqual(stats["top_products"][0]["units"], 3)
        self.assertEqual(stats["daily"][-1]["count"], 3)
        courier_names = [c.name for c in stats["couriers"]]
        self.assertIn("Ерлан", courier_names)
        self.assertNotIn("Бывший", courier_names)


class OrderAdminTests(DeliveryTestCase):
    def setUp(self):
        self.client.force_login(self.make_staff("operator", OPERATOR))

    def test_changelist_opens(self):
        self.make_order()
        response = self.client.get(reverse("admin:delivery_order_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Статистика</a>")

    def test_assigning_courier_hands_order_over(self):
        # Курьеру передаётся только готовый заказ
        order = self.make_order(status=Order.Status.READY)
        url = reverse("admin:delivery_order_change", args=[order.pk])
        response = self.client.get(url)
        data = {
            "client": order.client_id,
            "courier": self.courier.pk,
            "status": order.status,
            "address": order.address,
            "total": order.total,
            "comment": "",
            "items-TOTAL_FORMS": 1,
            "items-INITIAL_FORMS": 1,
            "items-MIN_NUM_FORMS": 0,
            "items-MAX_NUM_FORMS": 1000,
            "items-0-id": order.items.first().pk,
            "items-0-order": order.pk,
            "items-0-product": self.pizza.pk,
            "items-0-quantity": 2,
            "items-0-price": "2900",
        }
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.HANDED_TO_COURIER)
        self.assertEqual(order.total, Decimal("5800"))

    def test_inactive_courier_not_offered(self):
        order = self.make_order()
        response = self.client.get(reverse("admin:delivery_order_change", args=[order.pk]))
        self.assertNotContains(response, "Бывший")

    def test_accept_action_only_touches_new_orders(self):
        new = self.make_order()
        delivered = self.make_order(status=Order.Status.DELIVERED)
        self.client.post(
            reverse("admin:delivery_order_changelist"),
            {"action": "accept_orders", "_selected_action": [new.pk, delivered.pk]},
        )
        new.refresh_from_db()
        delivered.refresh_from_db()
        self.assertEqual(new.status, Order.Status.ACCEPTED)
        self.assertEqual(delivered.status, Order.Status.DELIVERED)

    def test_cancel_action_skips_delivered(self):
        delivered = self.make_order(status=Order.Status.DELIVERED)
        in_transit = self.make_order(status=Order.Status.IN_TRANSIT)
        self.client.post(
            reverse("admin:delivery_order_changelist"),
            {"action": "cancel_orders", "_selected_action": [delivered.pk, in_transit.pk]},
        )
        delivered.refresh_from_db()
        in_transit.refresh_from_db()
        self.assertEqual(delivered.status, Order.Status.DELIVERED)
        self.assertEqual(in_transit.status, Order.Status.CANCELLED)


class PaymentTests(DeliveryTestCase):
    """Оплата в Telegram: проверка перед списанием и отметка об оплате (delivery/payments.py)."""

    def pay(self, order, telegram_id=1, total=None, currency="KZT", charge="tg_1"):
        total = payments.amount(order.total) if total is None else total
        return payments.mark_paid(payments.invoice_payload(order), telegram_id, total, currency, charge, "ch_1")

    def test_amount_in_tiyn(self):
        self.assertEqual(payments.amount(Decimal("2900.00")), 290000)

    def test_check_allows_correct_payment(self):
        order = self.make_order(quantity=2)  # 5 800 ₸ — доставка бесплатная
        self.assertIsNone(payments.check_before_payment(payments.invoice_payload(order), 1, 580000, "KZT"))
        small = self.make_order(quantity=1)  # 2 900 ₸ + 500 ₸ доставки — один счёт на всё
        self.assertIsNone(payments.check_before_payment(payments.invoice_payload(small), 1, 340000, "KZT"))

    def test_check_rejects_wrong_amount_foreign_cancelled(self):
        order = self.make_order()
        payload = payments.invoice_payload(order)
        self.assertIn("Сумма", payments.check_before_payment(payload, 1, 100, "KZT"))
        self.assertIn("не найден", payments.check_before_payment("delivery:1", 1, 290000, "KZT"))
        self.assertIn("не найден", payments.check_before_payment(payload, 999, 290000, "KZT"))
        self.assertIn("не найден", payments.check_before_payment("order:abc", 1, 290000, "KZT"))
        cancelled = self.make_order(status=Order.Status.CANCELLED)
        self.assertIn("отменён", payments.check_before_payment(payments.invoice_payload(cancelled), 1, 290000, "KZT"))

    def test_mark_paid_once(self):
        order = self.make_order()
        self.assertTrue(self.pay(order))
        order.refresh_from_db()
        self.assertEqual(order.payment_status, Order.PaymentStatus.PAID)
        self.assertEqual(order.telegram_charge_id, "tg_1")
        self.assertFalse(self.pay(order, charge="tg_2"))  # повторное сообщение о платеже
        order.refresh_from_db()
        self.assertEqual(order.telegram_charge_id, "tg_1")
        self.assertIn("уже оплачен", payments.check_before_payment(payments.invoice_payload(order), 1, 290000, "KZT"))

    def test_foreign_client_cannot_mark_paid(self):
        order = self.make_order()
        self.assertFalse(self.pay(order, telegram_id=999))
        order.refresh_from_db()
        self.assertEqual(order.payment_status, Order.PaymentStatus.UNPAID)

    def test_old_code_insert_gets_unpaid_default(self):
        # Бот со старым кодом не знает новых колонок — база сама ставит «не оплачен»
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO delivery_order (client_id, status, address, total, comment, created_at, updated_at)"
                " VALUES (%s, 'new', 'старый бот', 0, '', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                [self.client_obj.pk],
            )
        order = Order.objects.get(address="старый бот")
        self.assertEqual(order.payment_status, Order.PaymentStatus.UNPAID)
        self.assertEqual(order.telegram_charge_id, "")


class DeliveryFeeTests(DeliveryTestCase):
    """Доставка 500 ₸, бесплатно от 5 000 ₸ — входит в сумму заказа."""

    def test_fee_added_below_threshold(self):
        order = self.make_order(quantity=1)
        self.assertEqual(order.items_total, Decimal("2900"))
        self.assertEqual(order.delivery_fee, Decimal("500"))
        self.assertEqual(order.total, Decimal("3400"))

    def test_free_from_threshold(self):
        order = self.make_order(quantity=2)
        self.assertEqual(order.delivery_fee, Decimal("0"))
        self.assertEqual(order.total, Decimal("5800"))

    @override_settings(DELIVERY={"fee": Decimal("700"), "free_from": Decimal("10000")})
    def test_rules_come_from_settings(self):
        order = self.make_order(quantity=2)
        self.assertEqual(order.total, Decimal("6500"))


class GeolocationTests(DeliveryTestCase):
    def test_map_link_only_with_coordinates(self):
        order = self.make_order()
        self.assertEqual(order.map_url, "")
        order.latitude, order.longitude = Decimal("43.238949"), Decimal("76.889709")
        self.assertEqual(order.map_url, "https://www.google.com/maps?q=43.238949,76.889709")

    def test_address_text_is_optional(self):
        order = Order.objects.create(client=self.client_obj, latitude=Decimal("43.2"), longitude=Decimal("76.9"))
        self.assertEqual(order.address, "")


class KitchenTests(DeliveryTestCase):
    def setUp(self):
        self.client.force_login(self.make_staff("cook", KITCHEN))
        self.url = reverse("admin:delivery_kitchenorder_changelist")

    def test_kitchen_sees_only_its_orders(self):
        visible = [self.make_order(status=s) for s in Order.KITCHEN_STATUSES]
        hidden = [self.make_order(status=s) for s in (Order.Status.NEW, Order.Status.IN_TRANSIT, Order.Status.CANCELLED)]
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        shown = set(response.context["cl"].queryset.values_list("pk", flat=True))
        self.assertEqual(shown, {o.pk for o in visible})
        self.assertFalse(shown & {o.pk for o in hidden})

    def test_kitchen_cannot_open_orders_or_products(self):
        self.assertEqual(self.client.get(reverse("admin:delivery_order_changelist")).status_code, 403)
        self.assertEqual(self.client.get(reverse("admin:delivery_product_changelist")).status_code, 403)

    def test_actions_move_order_from_accepted_to_ready(self):
        order = self.make_order(status=Order.Status.ACCEPTED)
        for action, expected in (("start_cooking", Order.Status.COOKING),
                                 ("start_packing", Order.Status.PACKING),
                                 ("mark_ready", Order.Status.READY)):
            self.client.post(self.url, {"action": action, "_selected_action": [order.pk]})
            order.refresh_from_db()
            self.assertEqual(order.status, expected)

    def test_ready_skips_orders_not_cooking(self):
        order = self.make_order(status=Order.Status.ACCEPTED)
        self.client.post(self.url, {"action": "mark_ready", "_selected_action": [order.pk]})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.ACCEPTED)

    def test_status_choices_limited_to_kitchen(self):
        self.make_order(status=Order.Status.COOKING)
        response = self.client.get(self.url)
        values = {value for value, _ in response.context["cl"].formset.forms[0].fields["status"].choices}
        self.assertEqual(values, set(Order.KITCHEN_STATUSES))


class ShopDisabledTests(TestCase):
    def test_root_redirects_to_panel(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/admin/", fetch_redirect_response=False)
        self.assertEqual(self.client.get("/menu/").status_code, 404)


class LanguageTests(DeliveryTestCase):
    """Панель на трёх языках: переключатель в шапке сохраняет выбор."""

    def setUp(self):
        self.client.force_login(self.make_staff("boss", MANAGER))

    def switch(self, code):
        self.client.post(reverse("set_language"), {"language": code, "next": "/admin/"})

    def test_switcher_in_header(self):
        response = self.client.get(reverse("admin:index"))
        for code in ("ru", "kk", "en"):
            self.assertContains(response, f'value="{code}"')

    def test_kazakh_and_english(self):
        self.make_order(status=Order.Status.COOKING)
        self.switch("kk")
        response = self.client.get(reverse("admin:delivery_order_changelist"))
        self.assertContains(response, "Тапсырыстар")
        self.assertContains(response, "Дайындалуда")
        self.switch("en")
        response = self.client.get(reverse("admin:delivery_kitchenorder_changelist"))
        self.assertContains(response, "Kitchen")
        self.assertContains(response, "Start cooking")

    def test_statistics_page_translated(self):
        self.switch("en")
        response = self.client.get(reverse("admin:delivery_order_statistics"))
        self.assertContains(response, "Average order")
