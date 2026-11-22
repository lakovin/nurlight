from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


class DeliveryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "delivery"
    verbose_name = _("Доставка")

    def ready(self):
        from .roles import ensure_roles

        post_migrate.connect(ensure_roles, sender=self)
