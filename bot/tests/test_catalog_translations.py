from io import StringIO

from asgiref.sync import sync_to_async
from django.core.management import call_command
from delivery.models import Category, Product

from bot.i18n import current_lang, localized
from bot.keyboards.catalog import categories_keyboard, products_keyboard
from bot.services.my_orders import get_order_for_client
from bot.tests.helpers import TG_ID, BotTestCase


def button_texts(markup):
    return [button.text for row in markup.inline_keyboard for button in row]


class LocalizedTests(BotTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.addCleanup(current_lang.set, "ru")

    async def test_falls_back_to_russian_when_no_translation(self):
        for lang in ("ru", "kk", "en"):
            self.assertEqual(localized(self.pizza, "name", lang), "Маргарита")

    async def test_returns_translation_when_filled(self):
        self.category.name_kk = "Сусындар"
        self.category.name_en = "Drinks"
        self.pizza.name_en = "Margherita"
        self.pizza.description = "Томатный соус"
        self.pizza.description_kk = "Қызанақ тұздығы"

        self.assertEqual(localized(self.category, "name", "kk"), "Сусындар")
        self.assertEqual(localized(self.category, "name", "en"), "Drinks")
        self.assertEqual(localized(self.category, "name", "ru"), "Пицца")
        self.assertEqual(localized(self.pizza, "name", "en"), "Margherita")
        self.assertEqual(localized(self.pizza, "name", "kk"), "Маргарита")  # нет перевода
        self.assertEqual(localized(self.pizza, "description", "kk"), "Қызанақ тұздығы")
        self.assertEqual(localized(self.pizza, "description", "en"), "Томатный соус")

    async def test_blank_translation_counts_as_missing(self):
        self.pizza.name_kk = "   "
        self.assertEqual(localized(self.pizza, "name", "kk"), "Маргарита")

    async def test_uses_current_language_by_default(self):
        self.pizza.name_en = "Margherita"
        current_lang.set("en")
        self.assertEqual(localized(self.pizza, "name"), "Margherita")


class KeyboardTranslationTests(BotTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.addCleanup(current_lang.set, "ru")

    async def test_category_and_product_buttons_follow_language(self):
        await Category.objects.filter(pk=self.category.pk).aupdate(name_kk="Сусындар")
        await Product.objects.filter(pk=self.pizza.pk).aupdate(name_kk="Маргарита (қаз.)")
        category = await Category.objects.aget(pk=self.category.pk)
        products = [p async for p in Product.objects.filter(category=category).order_by("-is_available", "name")]

        current_lang.set("kk")
        self.assertIn("Сусындар", button_texts(categories_keyboard([category])))
        self.assertTrue(any("Маргарита (қаз.)" in text for text in button_texts(products_keyboard(products))))

        current_lang.set("ru")
        self.assertIn("Пицца", button_texts(categories_keyboard([category])))

    async def test_order_card_items_use_client_language(self):
        await Product.objects.filter(pk=self.pizza.pk).aupdate(name_en="Margherita")
        order = await self.make_order(self.pizza)

        current_lang.set("en")
        card = await get_order_for_client(TG_ID, order.pk)
        self.assertEqual(card["items"][0]["name"], "Margherita")


class FillTranslationsCommandTests(BotTestCase):
    @staticmethod
    def run_command() -> str:
        out = StringIO()
        call_command("fill_translations", stdout=out)
        return out.getvalue()

    async def test_fills_known_names_and_keeps_existing_translations(self):
        drinks = await Category.objects.acreate(name="Напитки", name_kk="Мой перевод")
        pizza = await Product.objects.acreate(
            name="Маргарита", price=2900, category=self.category, name_kk="Моя Маргарита"
        )
        unknown = await Product.objects.acreate(name="Неизвестный", price=100, category=self.category)

        await sync_to_async(self.run_command)()

        await drinks.arefresh_from_db()
        await pizza.arefresh_from_db()
        await unknown.arefresh_from_db()

        self.assertEqual(drinks.name_kk, "Мой перевод")  # введённое не затёрто
        self.assertEqual(drinks.name_en, "Drinks")  # пустое заполнено
        self.assertEqual(pizza.name_kk, "Моя Маргарита")
        self.assertEqual(pizza.name_en, "Margherita")
        self.assertEqual(unknown.name_kk, "")  # неизвестные товары не трогаем

    async def test_second_run_changes_nothing(self):
        await Product.objects.acreate(name="Морс клюквенный", price=700, category=self.category)
        await sync_to_async(self.run_command)()
        output = await sync_to_async(self.run_command)()
        self.assertIn("товаров: 0", output)
