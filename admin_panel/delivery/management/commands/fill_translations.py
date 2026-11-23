"""Заполняет переводы названий и описаний (казахский и английский) для известного каталога.

    python manage.py fill_translations

Работает так:
- берёт только пустые поля переводов: то, что уже введено в панели, не перезаписывается;
- находит категорию или товар по русскому названию (имя должно совпасть точно);
- товары и категории, которых нет в списке ниже, не трогает: их переводы вводят в панели
  (раздел «Переводы для бота»).

Казахские тексты нужно проверить носителю языка.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from delivery.models import Category, Product

CATEGORIES = {
    "Пицца": {"name_kk": "Пицца", "name_en": "Pizza"},
    "Напитки": {"name_kk": "Сусындар", "name_en": "Drinks"},
}

PRODUCTS = {
    "Маргарита": {
        "name_kk": "Маргарита",
        "name_en": "Margherita",
        "description_kk": "Қызанақ тұздығы, моцарелла, базилик",
        "description_en": "Tomato sauce, mozzarella, basil",
    },
    "Пепперони": {
        "name_kk": "Пепперони",
        "name_en": "Pepperoni",
        "description_kk": "Қызанақ тұздығы, моцарелла, пепперони",
        "description_en": "Tomato sauce, mozzarella, pepperoni",
    },
    "Айран 0,5 л": {
        "name_kk": "Айран 0,5 л",
        "name_en": "Ayran 0.5 l",
    },
    "Морс клюквенный": {
        "name_kk": "Мүкжидек морсы",
        "name_en": "Cranberry fruit drink",
        "description_kk": "Үйде жасалған, 0,4 л",
        "description_en": "Homemade, 0.4 l",
    },
}


def fill(model, translations: dict) -> int:
    """Заполняет пустые переводы; возвращает число обновлённых строк."""
    updated = 0

    for obj in model.objects.filter(name__in=translations):
        changes = {
            field: text
            for field, text in translations[obj.name].items()
            if not (getattr(obj, field) or "").strip()
        }

        if changes:
            for field, text in changes.items():
                setattr(obj, field, text)

            obj.save(update_fields=list(changes))
            updated += 1

    return updated


class Command(BaseCommand):
    help = "Заполняет пустые переводы названий и описаний для известного каталога"

    @transaction.atomic
    def handle(self, *args, **options):
        categories = fill(Category, CATEGORIES)
        products = fill(Product, PRODUCTS)

        self.stdout.write(
            self.style.SUCCESS(
                f"Обновлено категорий: {categories}, товаров: {products}."
            )
        )
