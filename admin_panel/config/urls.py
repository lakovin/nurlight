from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Nurlight — панель оператора"
admin.site.site_title = "Nurlight"
admin.site.index_title = "Управление заказами"

urlpatterns = [
    path("admin/", admin.site.urls),
    # Сайт для клиентов: каталог, корзина, оформление и статус заказа
    path("", include("shop.urls")),
]
