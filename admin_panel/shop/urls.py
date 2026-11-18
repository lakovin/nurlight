from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("menu/", views.catalog, name="catalog"),
    path("cart/", views.checkout, name="checkout"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("order/", views.order_lookup, name="order_lookup"),
    path("order/<int:pk>/", views.order_status, name="order_status"),
    path("assistant/", views.assistant_chat, name="assistant"),
]
