from django.conf import settings

from .cart import Cart


def shop(request):
    return {"cart_count": Cart(request).count, "shop": settings.SHOP}
