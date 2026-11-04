from django.db import models


class Language(models.TextChoices):
    RU = "ru", "Русский"
    KK = "kk", "Қазақша"


class Client(models.Model):
    telegram_id = models.BigIntegerField("Telegram ID", unique=True)
    name = models.CharField("Имя", max_length=255)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    language = models.CharField("Язык", max_length=2, choices=Language.choices, default=Language.RU)
    registered_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f"{self.name} ({self.phone or self.telegram_id})"


class Category(models.Model):
    name = models.CharField("Название", max_length=255)
    sort_order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products", verbose_name="Категория"
    )
    is_available = models.BooleanField("Доступен", default=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["category", "name"]

    def __str__(self):
        return self.name


class Courier(models.Model):
    name = models.CharField("Имя", max_length=255)
    phone = models.CharField("Телефон", max_length=32)
    telegram_id = models.BigIntegerField("Telegram ID", unique=True, null=True, blank=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Курьер"
        verbose_name_plural = "Курьеры"

    def __str__(self):
        return self.name


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        ACCEPTED = "accepted", "Принят"
        HANDED_TO_COURIER = "handed_to_courier", "Передан курьеру"
        IN_TRANSIT = "in_transit", "В пути"
        DELIVERED = "delivered", "Доставлен"
        CANCELLED = "cancelled", "Отменён"

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="orders", verbose_name="Клиент")
    courier = models.ForeignKey(
        Courier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Курьер",
    )
    status = models.CharField("Статус", max_length=32, choices=Status.choices, default=Status.NEW)
    address = models.CharField("Адрес", max_length=500)
    total = models.DecimalField("Сумма", max_digits=10, decimal_places=2, default=0)
    comment = models.TextField("Комментарий", blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    @property
    def number(self):
        # Номер заказа для клиента — тот же id, но в читаемом виде
        return f"{self.pk:06d}"

    def __str__(self):
        return f"Заказ №{self.number}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="+", verbose_name="Товар")
    quantity = models.PositiveIntegerField("Количество", default=1)
    price = models.DecimalField("Цена на момент заказа", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product} × {self.quantity}"


class FAQ(models.Model):
    question = models.CharField("Вопрос", max_length=500)
    answer = models.TextField("Ответ")
    language = models.CharField("Язык", max_length=2, choices=Language.choices, default=Language.RU)

    class Meta:
        verbose_name = "Частый вопрос"
        verbose_name_plural = "Частые вопросы"

    def __str__(self):
        return self.question
