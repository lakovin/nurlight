from datetime import timedelta

from aiogram.exceptions import TelegramForbiddenError
from aiogram.methods import SendMessage
from delivery.models import Order
from django.utils import timezone

from bot import tests_i18n
from bot.i18n import LANGS, TEXTS, current_lang, status_label, t, variants
from bot.services import notifications as n
from bot.tests.helpers import TG_ID, BotTestCase


class FakeBot:
    """Заменяет Telegram: запоминает отправленные сообщения."""

    def __init__(self, blocked=False):
        self.sent = []
        self.blocked = blocked

    async def send_message(self, chat_id, text, reply_markup=None):
        if self.blocked:
            raise TelegramForbiddenError(
                method=SendMessage(chat_id=chat_id, text=text),
                message="Forbidden: bot was blocked by the user",
            )
        self.sent.append((chat_id, text))


class NotificationTests(BotTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        n._known.clear()
        n._attempts.clear()
        self.bot = FakeBot()

    async def start_bot_with(self, order):
        """Бот «запущен» после создания заказа: статус заказа считается известным."""
        self.started = timezone.now() + timedelta(seconds=1)
        await n.poll_once(self.bot, self.started)
        self.assertEqual(self.bot.sent, [])

    async def set_status(self, order, status):
        await Order.objects.filter(pk=order.pk).aupdate(status=status)
        self.bot.sent.clear()
        await n.poll_once(self.bot, self.started)

    async def test_status_change_sends_one_message(self):
        order = await self.make_order()
        await self.start_bot_with(order)

        await self.set_status(order, Order.Status.ACCEPTED)
        self.assertEqual(len(self.bot.sent), 1)
        self.assertEqual(self.bot.sent[0][0], TG_ID)
        # в сообщении номер среди заказов клиента, а не общий номер из панели
        self.assertIn("№1", self.bot.sent[0][1])
        self.assertNotIn(order.number, self.bot.sent[0][1])

        self.bot.sent.clear()
        await n.poll_once(self.bot, self.started)  # повторная проверка
        self.assertEqual(self.bot.sent, [])

    async def test_packing_has_no_message_but_ready_has(self):
        order = await self.make_order()
        await self.start_bot_with(order)

        await self.set_status(order, Order.Status.PACKING)
        self.assertEqual(self.bot.sent, [])

        await self.set_status(order, Order.Status.READY)
        self.assertEqual(len(self.bot.sent), 1)

    async def test_final_status_is_notified(self):
        order = await self.make_order()
        await self.start_bot_with(order)
        await self.set_status(order, Order.Status.IN_TRANSIT)
        await self.set_status(order, Order.Status.DELIVERED)
        self.assertEqual(len(self.bot.sent), 1)

    async def test_blocked_bot_is_not_retried(self):
        order = await self.make_order()
        await self.start_bot_with(order)
        self.bot.blocked = True

        await Order.objects.filter(pk=order.pk).aupdate(status=Order.Status.ACCEPTED)
        await n.poll_once(self.bot, self.started)
        await n.poll_once(self.bot, self.started)
        self.assertEqual(self.bot.sent, [])
        self.assertEqual(n._known[order.pk], str(Order.Status.ACCEPTED))

    async def test_client_cancel_in_bot_is_not_duplicated(self):
        order = await self.make_order()
        await self.start_bot_with(order)

        n.mark_known(order.pk, Order.Status.CANCELLED)
        await self.set_status(order, Order.Status.CANCELLED)
        self.assertEqual(self.bot.sent, [])

    async def test_message_language_follows_client_profile(self):
        from delivery.models import Client

        order = await self.make_order()
        await Client.objects.filter(telegram_id=TG_ID).aupdate(language="kk")
        await self.start_bot_with(order)

        await self.set_status(order, Order.Status.ACCEPTED)
        self.assertIn("тапсырыс қабылданды", self.bot.sent[0][1])

    def test_detect_changes_ignores_old_unknown_orders(self):
        started = timezone.now()
        rows = [(1, "accepted", 10, started - timedelta(days=1), "ru")]
        known = {}
        self.assertEqual(n.detect_changes(known, rows, started), [])
        self.assertEqual(known[1], "accepted")

    def test_detect_changes_new_order_accepted_before_first_poll(self):
        started = timezone.now() - timedelta(minutes=5)
        rows = [(2, "accepted", 10, timezone.now(), "en")]
        changes = n.detect_changes({}, rows, started)
        self.assertEqual(changes, [(2, 10, "accepted", "en")])


class TranslationTests(BotTestCase):
    def test_every_key_has_all_languages_and_same_placeholders(self):
        self.assertEqual(tests_i18n.check_texts(), [])

    def test_no_missing_keys_in_code(self):
        self.assertEqual(tests_i18n.check_keys_used(), [])

    def test_no_untranslated_strings(self):
        self.assertEqual(tests_i18n.check_hardcoded_russian(), [])

    def test_translation_returns_each_language(self):
        texts = {t("btn_cart", lang) for lang in LANGS}
        self.assertEqual(len(texts), 3)

    def test_current_language_is_used_by_default(self):
        current_lang.set("en")
        self.assertEqual(t("btn_cart"), TEXTS["btn_cart"]["en"])
        current_lang.set("ru")

    def test_unknown_language_falls_back_to_russian(self):
        self.assertEqual(t("btn_cart", "de"), TEXTS["btn_cart"]["ru"])

    def test_menu_button_variants_include_all_languages(self):
        self.assertEqual(variants("btn_cart"), set(TEXTS["btn_cart"].values()))
        self.assertIn("🤖 AI-помощник", variants("btn_ai"))  # старая кнопка

    def test_status_labels_exist_for_every_order_status(self):
        for status in Order.Status.values:
            for lang in LANGS:
                self.assertNotEqual(status_label(status, lang), status, f"{status}/{lang}")
