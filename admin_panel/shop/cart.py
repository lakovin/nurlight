from dataclasses import dataclass
from decimal import Decimal

from delivery.models import Product

SESSION_KEY = "cart"
MAX_QUANTITY = 99


@dataclass
class CartLine:
    product: Product
    quantity: int

    @property
    def sum(self) -> Decimal:
        return self.product.price * self.quantity


class Cart:
    """Корзина в сессии посетителя: {id товара: количество}. В базу попадает только при оформлении."""

    def __init__(self, request):
        self.session = request.session
        self.data: dict[str, int] = self.session.get(SESSION_KEY, {})

    def _save(self):
        self.session[SESSION_KEY] = self.data
        self.session.modified = True

    def change(self, product_id: int, delta: int):
        key = str(product_id)
        quantity = min(self.data.get(key, 0) + delta, MAX_QUANTITY)
        if quantity > 0:
            self.data[key] = quantity
        else:
            self.data.pop(key, None)
        self._save()

    def remove(self, product_id: int):
        self.data.pop(str(product_id), None)
        self._save()

    def clear(self):
        self.data = {}
        self._save()

    @property
    def count(self) -> int:
        return sum(self.data.values())

    def lines(self) -> list[CartLine]:
        products = Product.objects.filter(pk__in=self.data.keys(), is_available=True).select_related("category")
        lines = [CartLine(p, self.data[str(p.pk)]) for p in products]
        # Товар сняли с продажи или удалили — убираем его из корзины
        if len(lines) != len(self.data):
            self.data = {str(line.product.pk): line.quantity for line in lines}
            self._save()
        return lines

    @staticmethod
    def total(lines: list[CartLine]) -> Decimal:
        return sum((line.sum for line in lines), start=Decimal(0))
