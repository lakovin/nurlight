from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView

admin.site.site_header = _("Nurlight — панель оператора")
admin.site.site_title = "Nurlight"
admin.site.index_title = _("Управление заказами")
admin.site.site_url = None  # клиентского сайта нет — ссылку «Открыть сайт» не показываем

urlpatterns = [
    path("admin/", admin.site.urls),
    # Переключатель языка панели: русский, казахский, английский
    path("i18n/", include("django.conf.urls.i18n")),
]

# Клиентского сайта в новой модели нет: клиенты заказывают в боте, а реклама для бизнеса —
# отдельная визитка (папка landing/). Код магазина (shop) оставлен, включается SHOP_ENABLED=1.
if settings.SHOP_ENABLED:
    urlpatterns.append(path("", include("shop.urls")))
else:
    urlpatterns.append(path("", RedirectView.as_view(url="/admin/", permanent=False)))
