"""Роли пользователей панели.

Группы создаются и обновляются автоматически после каждого `migrate`.
Чтобы выдать роль, отметьте у пользователя «Статус персонала» и добавьте
его в группу «Оператор», «Руководитель» или «Кухня».
"""
from django.contrib.auth.models import Group, Permission

OPERATOR = "Оператор"
MANAGER = "Руководитель"
KITCHEN = "Кухня"

# Кухня видит только раздел «Кухня»: заказы от «Принят» до «Готов», меняет их статус
KITCHEN_PERMISSIONS = ["view_kitchenorder", "change_kitchenorder"]

# Оператор обрабатывает заказы: принимает, меняет статус, назначает курьера.
# Справочники (товары, курьеры, FAQ) он только просматривает.
OPERATOR_PERMISSIONS = [
    "view_order", "add_order", "change_order",
    "view_orderitem", "add_orderitem", "change_orderitem", "delete_orderitem",
    "view_client", "add_client", "change_client",
    "view_courier",
    "view_product", "view_category",
    "view_faq",
    "view_kitchenorder", "change_kitchenorder",
]


def ensure_roles(**kwargs):
    delivery_perms = Permission.objects.filter(content_type__app_label="delivery")

    operator, _ = Group.objects.get_or_create(name=OPERATOR)
    operator.permissions.set(delivery_perms.filter(codename__in=OPERATOR_PERMISSIONS))

    # Руководитель может всё в разделе «Доставка», включая статистику
    manager, _ = Group.objects.get_or_create(name=MANAGER)
    manager.permissions.set(delivery_perms)

    kitchen, _ = Group.objects.get_or_create(name=KITCHEN)
    kitchen.permissions.set(delivery_perms.filter(codename__in=KITCHEN_PERMISSIONS))
