"""Демо-данные для разработки, тестирования и скриншотов.

python manage.py seed_demo           — каталог, курьеры, клиенты, заказы за 14 дней и пользователи панели
python manage.py seed_demo --orders 100
Повторный запуск добавляет ещё заказы, справочники не дублируются.
"""
import random
from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from delivery.models import Client, Courier, Order, OrderItem, Product
from delivery.roles import MANAGER, OPERATOR

DEMO_PASSWORD = "nurlight-demo"
DEMO_USERS = [("manager", MANAGER), ("operator", OPERATOR)]

COURIERS = [("Ерлан", "+77011234567"), ("Данияр", "+77021234567"), ("Асель", "+77031234567")]
CLIENTS = ["Айгерим", "Тимур", "Мадина", "Алихан", "Жанна", "Руслан", "Дана", "Арман"]
STREETS = ["Абая", "Толе би", "Сатпаева", "Розыбакиева", "Жандосова", "Тимирязева", "Байтурсынова"]

# Чем старше заказ, тем вероятнее он уже доставлен
OLD_ORDER_STATUSES = [Order.Status.DELIVERED] * 8 + [Order.Status.CANCELLED]
TODAY_STATUSES = list(Order.Status.values)


class Command(BaseCommand):
    help = "Заполняет базу демо-данными"

    def add_arguments(self, parser):
        parser.add_argument("--orders", type=int, default=60)
        parser.add_argument("--seed", type=int, default=None, help="для повторяемого результата")

    @transaction.atomic
    def handle(self, *args, orders, seed, **options):
        rng = random.Random(seed)
        call_command("loaddata", "demo_catalog", verbosity=0)
        products = list(Product.objects.filter(is_available=True))

        couriers = [
            Courier.objects.get_or_create(phone=phone, defaults={"name": name})[0] for name, phone in COURIERS
        ]
        clients = [
            Client.objects.get_or_create(
                telegram_id=1000 + i, defaults={"name": name, "phone": f"+7705{i:07d}"}
            )[0]
            for i, name in enumerate(CLIENTS)
        ]

        now = timezone.now()
        for _ in range(orders):
            days_ago = min(int(rng.expovariate(1 / 5)), 13)
            created = now - timedelta(days=days_ago, minutes=rng.randint(0, 600))
            status = rng.choice(TODAY_STATUSES if days_ago == 0 else OLD_ORDER_STATUSES)
            has_courier = status in (
                Order.Status.HANDED_TO_COURIER,
                Order.Status.IN_TRANSIT,
                Order.Status.DELIVERED,
            )
            order = Order.objects.create(
                client=rng.choice(clients),
                courier=rng.choice(couriers) if has_courier else None,
                status=status,
                address=f"ул. {rng.choice(STREETS)}, {rng.randint(1, 200)}, кв. {rng.randint(1, 120)}",
            )
            for product in rng.sample(products, k=rng.randint(1, min(3, len(products)))):
                OrderItem.objects.create(
                    order=order, product=product, quantity=rng.randint(1, 3), price=product.price
                )
            order.recalculate_total()
            # created_at ставится автоматически, поэтому дату в прошлом задаём отдельным запросом
            Order.objects.filter(pk=order.pk).update(created_at=created, updated_at=created)

        for username, group_name in DEMO_USERS:
            user, created = User.objects.get_or_create(username=username, defaults={"is_staff": True})
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
            user.groups.add(Group.objects.get(name=group_name))

        self.stdout.write(self.style.SUCCESS(f"Добавлено заказов: {orders}."))
        self.stdout.write(
            f"Пользователи панели: manager (руководитель), operator (оператор), пароль {DEMO_PASSWORD}"
        )
