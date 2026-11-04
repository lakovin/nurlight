from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

admin.site.site_header = "Nurlight — панель оператора"
admin.site.site_title = "Nurlight"
admin.site.index_title = "Управление заказами"

urlpatterns = [
    path("", RedirectView.as_view(url="/admin/", permanent=False)),
    path("admin/", admin.site.urls),
]
