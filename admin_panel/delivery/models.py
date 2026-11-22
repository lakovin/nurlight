from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Language(models.TextChoices):
    RU = "ru", _("Русский")
    KK = "kk", _("Қазақша")


class Client(models.Model):
    # Пусто у клиентов, которые заказали через сайт и не писали боту
    telegram_id = models.BigIntegerField("Telegram ID", unique=True, null=True, blank=True)
    name = models.CharField(_("Имя"), max_length=255)
    phone = models.CharField(_("Телефон"), max_length=32, blank=True)
    language = models.CharField(_("Язык"), max_length=2, choices=Language.choices, default=Language.RU)
    registered_at = models.DateTimeField(_("Дата регистрации"), auto_now_add=True)

    class Meta:
        verbose_name = _("Клиент")
        verbose_name_plural = _("Клиенты")

    def __str__(self):
        return f"{self.name} ({self.phone or self.telegram_id})"


class Category(models.Model):
    name = models.CharField(_("Название"), max_length=255)
    sort_order = models.PositiveIntegerField(_("Порядок"), default=0)

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(_("Название"), max_length=255)
    description = models.TextField(_("Описание"), blank=True)
    price = models.DecimalField(_("Цена"), max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products", verbose_name=_("Категория")
    )
    is_available = models.BooleanField(_("Доступен"), default=True)

    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")
        ordering = ["category", "name"]

    def __str__(self):
        return self.name


class Courier(models.Model):
    name = models.CharField(_("Имя"), max_length=255)
    phone = models.CharField(_("Телефон"), max_length=32)
    telegram_id = models.BigIntegerField("Telegram ID", unique=True, null=True, blank=True)
    is_active = models.BooleanField(_("Активен"), default=True)

    class Meta:
        verbose_name = _("Курьер")
        verbose_name_plural = _("Курьеры")

    def __str__(self):
        return self.name


class PaymentStatus(models.TextChoices):
    UNPAID = "unpaid", _("Не оплачен")
    PAID = "paid", _("Оплачен")


class Order(models.Model):
    PaymentStatus = PaymentStatus

    class Status(models.TextChoices):
        NEW = "new", _("Новый")
        ACCEPTED = "accepted", _("Принят")
        # Кухня ведёт заказ от «Принят» до «Готов» (раздел «Кухня» в панели)
        COOKING = "cooking", _("Готовится")
        PACKING = "packing", _("Упаковывается")
        READY = "ready", _("Готов")
        HANDED_TO_COURIER = "handed_to_courier", _("Передан курьеру")
        IN_TRANSIT = "in_transit", _("В пути")
        DELIVERED = "delivered", _("Доставлен")
        CANCELLED = "cancelled", _("Отменён")

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="orders", verbose_name=_("Клиент"))
    courier = models.ForeignKey(
        Courier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name=_("Курьер"),
    )
    status = models.CharField(_("Статус"), max_length=32, choices=Status.choices, default=Status.NEW)
    # Клиент отправляет геолокацию в боте; адрес текстом — по желанию (подъезд, этаж, квартира)
    address = models.CharField(_("Адрес"), max_length=500, blank=True, default="", db_default="")
    latitude = models.DecimalField(_("Широта"), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_("Долгота"), max_digits=9, decimal_places=6, null=True, blank=True)
    total = models.DecimalField(_("Сумма"), max_digits=10, decimal_places=2, default=0)
    comment = models.TextField(_("Комментарий"), blank=True)
    # Оплата во встроенных платежах Telegram (провайдер Stripe), логика — delivery/payments.py.
    # db_default — чтобы бот со старым кодом (без этих полей) мог создавать заказы в общей базе
    payment_status = models.CharField(
        _("Оплата"), max_length=16, choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID, db_default=PaymentStatus.UNPAID,
    )
    paid_at = models.DateTimeField(_("Оплачен"), null=True, blank=True)
    # Номера платежа: по ним операция находится в Telegram и в кабинете Stripe (для возврата)
    telegram_charge_id = models.CharField(_("Платёж в Telegram"), max_length=255, blank=True, default="", db_default="")
    provider_charge_id = models.CharField(_("Платёж в Stripe"), max_length=255, blank=True, default="", db_default="")
    # Доставка входит в сумму заказа: settings.DELIVERY (500 ₸, бесплатно от 5 000 ₸), см. recalculate_total
    delivery_fee = models.DecimalField(_("Доставка"), max_digits=10, decimal_places=2, default=0, db_default=0)
    created_at = models.DateTimeField(_("Создан"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлён"), auto_now=True)

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        ordering = ["-created_at"]
        permissions = [("view_statistics", _("Может смотреть статистику"))]

    # Статусы, после которых заказ уже не меняется
    FINAL_STATUSES = (Status.DELIVERED, Status.CANCELLED)

    @property
    def number(self):
        # Номер заказа для клиента — тот же id, но в читаемом виде
        return f"{self.pk:06d}"

    # Статусы, которые ведёт кухня
    KITCHEN_STATUSES = (Status.ACCEPTED, Status.COOKING, Status.PACKING, Status.READY)

    @property
    def items_total(self):
        return sum((item.price * item.quantity for item in self.items.all()), start=Decimal(0))

    @property
    def map_url(self):
        if self.latitude is None or self.longitude is None:
            return ""
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"

    def recalculate_total(self):
        """Сумма = блюда + доставка. Доставка бесплатна от порога, иначе фиксированная цена."""
        items = self.items_total
        rules = settings.DELIVERY
        self.delivery_fee = Decimal(0) if items >= rules["free_from"] else rules["fee"]
        self.total = items + self.delivery_fee
        self.save(update_fields=["delivery_fee", "total", "updated_at"])

    def __str__(self):
        return _("Заказ №%(number)s") % {"number": self.number}


class KitchenOrder(Order):
    """Заказ глазами кухни: раздел «Кухня» в панели, только статусы от «Принят» до «Готов»."""

    class Meta:
        proxy = True
        verbose_name = _("Заказ на кухне")
        verbose_name_plural = _("Кухня")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name=_("Заказ"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="+", verbose_name=_("Товар"))
    quantity = models.PositiveIntegerField(_("Количество"), default=1)
    price = models.DecimalField(_("Цена на момент заказа"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Позиция заказа")
        verbose_name_plural = _("Позиции заказа")

    def __str__(self):
        return f"{self.product} × {self.quantity}"


class FAQ(models.Model):
    question = models.CharField(_("Вопрос"), max_length=500)
    answer = models.TextField(_("Ответ"))
    language = models.CharField(_("Язык"), max_length=2, choices=Language.choices, default=Language.RU)

    class Meta:
        verbose_name = _("Частый вопрос")
        verbose_name_plural = _("Частые вопросы")

    def __str__(self):
        return self.question
