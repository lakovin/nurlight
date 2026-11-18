import json
from decimal import Decimal
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from delivery.models import Category, Client, Courier, Order, OrderItem, Product

from .phones import normalize_phone
from .templatetags.shop_tags import money, plural_ru


class HelpersTests(TestCase):
    def test_normalize_phone(self):
        self.assertEqual(normalize_phone("8 (700) 111-22-33"), "+77001112233")
        self.assertEqual(normalize_phone("+7 700 111 22 33"), "+77001112233")
        self.assertEqual(normalize_phone("7001112233"), "+77001112233")
        self.assertIsNone(normalize_phone("12345"))
        self.assertIsNone(normalize_phone("+1 202 555 0100"))

    def test_money_and_plural(self):
        self.assertEqual(money(Decimal("2900.00")), "2 900 ₸")
        self.assertEqual(money(Decimal("12.50")), "12.50 ₸")
        self.assertEqual([plural_ru(n, "товар,товара,товаров") for n in (1, 3, 5, 11, 21)],
                         ["товар", "товара", "товаров", "товаров", "товар"])


class ShopTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        pizza = Category.objects.create(name="Пицца")
        drinks = Category.objects.create(name="Напитки", sort_order=1)
        cls.margarita = Product.objects.create(name="Маргарита", price=Decimal("2900"), category=pizza)
        cls.mors = Product.objects.create(name="Морс клюквенный", price=Decimal("700"), category=drinks)
        cls.hidden = Product.objects.create(name="Снятая с продажи", price=Decimal("100"), category=pizza, is_available=False)

    def add(self, product, times=1):
        for _ in range(times):
            self.client.post(reverse("shop:cart_add", args=[product.pk]))

    def checkout(self, **overrides):
        data = {"name": "Айгерим", "phone": "8 700 111 22 33", "address": "Абая 10, кв. 5", "comment": ""}
        data.update(overrides)
        return self.client.post(reverse("shop:checkout"), data)


class CatalogTests(ShopTestCase):
    def test_pages_open(self):
        for name in ("shop:home", "shop:catalog", "shop:checkout", "shop:order_lookup"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_catalog_hides_unavailable(self):
        response = self.client.get(reverse("shop:catalog"))
        self.assertContains(response, "Маргарита")
        self.assertNotContains(response, "Снятая с продажи")

    def test_filter_by_category_and_search(self):
        url = reverse("shop:catalog")
        drinks = self.mors.category
        response = self.client.get(url, {"category": drinks.pk})
        self.assertContains(response, "Морс")
        self.assertNotContains(response, "Маргарита</h3>")
        response = self.client.get(url, {"q": "марг"})
        self.assertContains(response, "Маргарита")
        self.assertNotContains(response, "Морс клюквенный</h3>")
        self.assertEqual(self.client.get(url, {"category": 999}).status_code, 404)


class CartTests(ShopTestCase):
    def test_add_and_change_quantity(self):
        self.add(self.margarita, 2)
        self.add(self.mors)
        self.assertEqual(self.client.session["cart"], {str(self.margarita.pk): 2, str(self.mors.pk): 1})
        self.client.post(reverse("shop:cart_update", args=[self.margarita.pk]), {"action": "dec"})
        self.client.post(reverse("shop:cart_update", args=[self.mors.pk]), {"action": "remove"})
        self.assertEqual(self.client.session["cart"], {str(self.margarita.pk): 1})
        response = self.client.get(reverse("shop:checkout"))
        self.assertContains(response, "Корзина · 1")

    def test_cannot_add_unavailable(self):
        response = self.client.post(reverse("shop:cart_add", args=[self.hidden.pk]))
        self.assertEqual(response.status_code, 404)

    def test_add_ignores_foreign_redirect(self):
        response = self.client.post(reverse("shop:cart_add", args=[self.margarita.pk]), {"next": "https://evil.example/"})
        self.assertEqual(response["Location"], reverse("shop:catalog"))


class CheckoutTests(ShopTestCase):
    def test_creates_order_for_web_client(self):
        self.add(self.margarita)
        self.add(self.mors, 2)
        response = self.checkout()
        order = Order.objects.get()
        self.assertRedirects(response, reverse("shop:order_status", args=[order.pk]))
        self.assertEqual(order.status, Order.Status.NEW)
        self.assertEqual(order.total, Decimal("4300"))
        self.assertEqual(order.client.phone, "+77001112233")
        self.assertIsNone(order.client.telegram_id)
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(self.client.session["cart"], {})

    def test_price_is_fixed_at_order_time(self):
        self.add(self.margarita)
        self.checkout()
        Product.objects.filter(pk=self.margarita.pk).update(price=Decimal("5000"))
        self.assertEqual(OrderItem.objects.get().price, Decimal("2900"))

    def test_reuses_client_with_same_phone(self):
        telegram_client = Client.objects.create(telegram_id=42, name="Из бота", phone="+77001112233")
        self.add(self.margarita)
        self.checkout()
        self.assertEqual(Order.objects.get().client, telegram_client)
        self.assertEqual(Client.objects.count(), 1)

    def test_invalid_phone_keeps_cart(self):
        self.add(self.margarita)
        response = self.checkout(phone="123")
        self.assertContains(response, "Укажите номер")
        self.assertFalse(Order.objects.exists())
        self.assertEqual(self.client.session["cart"], {str(self.margarita.pk): 1})

    def test_empty_cart_cannot_be_ordered(self):
        response = self.checkout()
        self.assertRedirects(response, reverse("shop:catalog"))
        self.assertFalse(Order.objects.exists())


class OrderStatusTests(ShopTestCase):
    def make_order(self, status=Order.Status.NEW):
        client = Client.objects.create(name="Айгерим", phone="+77001112233")
        order = Order.objects.create(client=client, address="Абая 10", status=status)
        OrderItem.objects.create(order=order, product=self.margarita, quantity=1, price=self.margarita.price)
        order.recalculate_total()
        return order

    def test_foreign_order_is_hidden(self):
        order = self.make_order()
        response = self.client.get(reverse("shop:order_status", args=[order.pk]))
        self.assertRedirects(response, reverse("shop:order_lookup"))

    def test_lookup_needs_matching_phone(self):
        order = self.make_order()
        url = reverse("shop:order_lookup")
        response = self.client.get(url, {"number": order.number, "phone": "+77009998877"})
        self.assertContains(response, "Заказ не найден")
        response = self.client.get(url, {"number": order.number, "phone": "87001112233"})
        self.assertRedirects(response, reverse("shop:order_status", args=[order.pk]))

    def test_timeline_follows_status(self):
        order = self.make_order(status=Order.Status.IN_TRANSIT)
        order.courier = Courier.objects.create(name="Ерлан", phone="+77012223344")
        order.save()
        self.client.get(reverse("shop:order_lookup"), {"number": order.number, "phone": "+77001112233"})
        response = self.client.get(reverse("shop:order_status", args=[order.pk]))
        states = [s["state"] for s in response.context["steps"]]
        self.assertEqual(states, ["done", "done", "done", "current", "todo"])
        self.assertContains(response, "Курьер: Ерлан")

    def test_cancelled_order(self):
        order = self.make_order(status=Order.Status.CANCELLED)
        self.client.get(reverse("shop:order_lookup"), {"number": order.number, "phone": "+77001112233"})
        response = self.client.get(reverse("shop:order_status", args=[order.pk]))
        self.assertEqual(response.context["steps"], [])
        self.assertContains(response, "Заказ отменён")


class AssistantTests(ShopTestCase):
    url = "/assistant/"

    def post(self, body):
        return self.client.post(self.url, data=json.dumps(body), content_type="application/json")

    def test_widget_on_every_page(self):
        for name in ("shop:home", "shop:catalog", "shop:checkout", "shop:order_lookup"):
            self.assertContains(self.client.get(reverse(name)), "Спросить ИИ")

    def test_answer_and_history(self):
        calls = []

        async def fake_ask(question, history):
            calls.append((question, list(history)))
            return f"ответ на «{question}»", True

        with mock.patch("shop.assistant.ask_ai", fake_ask):
            first = self.post({"message": "Что взять?"}).json()
            self.post({"message": "А дешевле?"})
        self.assertEqual(first, {"answer": "ответ на «Что взять?»", "ok": True})
        self.assertEqual(calls[1][1], [{"role": "user", "text": "Что взять?"}, {"role": "model", "text": "ответ на «Что взять?»"}])

    def test_failed_answer_not_saved(self):
        async def fail(question, history):
            return "⚠️ Сейчас не удалось связаться с AI.", False

        with mock.patch("shop.assistant.ask_ai", fail):
            data = self.post({"message": "привет"}).json()
        self.assertFalse(data["ok"])
        self.assertEqual(self.client.session.get("assistant_history", []), [])

    def test_clear_and_validation(self):
        session = self.client.session
        session["assistant_history"] = [{"role": "user", "text": "x"}]
        session.save()
        self.assertEqual(self.post({"action": "clear"}).status_code, 200)
        self.assertEqual(self.client.session["assistant_history"], [])
        self.assertEqual(self.post({"message": "  "}).status_code, 400)
        self.assertEqual(self.post({"message": "a" * 1001}).status_code, 400)
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_rate_limit(self):
        async def fake_ask(question, history):
            return "ок", True

        with mock.patch("shop.assistant.ask_ai", fake_ask):
            codes = [self.post({"message": f"вопрос {i}"}).status_code for i in range(21)]
        self.assertEqual(codes[:20], [200] * 20)
        self.assertEqual(codes[20], 429)

    def test_requires_csrf(self):
        from django.test import Client as HttpClient
        strict = HttpClient(enforce_csrf_checks=True)
        response = strict.post(self.url, data='{"message": "hi"}', content_type="application/json")
        self.assertEqual(response.status_code, 403)
