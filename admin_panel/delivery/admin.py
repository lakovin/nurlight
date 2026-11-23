from django.contrib import admin, messages
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import FAQ, Category, Client, Courier, KitchenOrder, Order, OrderItem, Product
from .statistics import statistics_view

def _map_link(order):
    if not order.map_url:
        return ""
    return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', order.map_url, _("Открыть на карте"))


def _place(order):
    """Адрес в списке: ссылка на геолокацию и уточнение текстом, если есть."""
    link = _map_link(order)
    if link and order.address:
        return format_html("{} · {}", link, order.address)
    return link or order.address or "—"


STATUS_COLORS = {
    Order.Status.NEW: "#d97706",
    Order.Status.ACCEPTED: "#2563eb",
    Order.Status.COOKING: "#ea580c",
    Order.Status.PACKING: "#ca8a04",
    Order.Status.READY: "#65a30d",
    Order.Status.HANDED_TO_COURIER: "#7c3aed",
    Order.Status.IN_TRANSIT: "#0891b2",
    Order.Status.DELIVERED: "#16a34a",
    Order.Status.CANCELLED: "#6b7280",
}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("product",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "created_at", "client", "place", "delivery_fee", "total", "payment_status", "status_badge", "status", "courier")
    list_display_links = ("number",)
    list_filter = ("status", "payment_status", "courier", "created_at")
    list_editable = ("status", "courier")
    list_select_related = ("client", "courier")
    search_fields = ("id", "address", "client__name", "client__phone")
    autocomplete_fields = ("client",)
    # Оплату отмечает только бот после платежа (delivery/payments.py), руками не меняется
    readonly_fields = ("created_at", "updated_at", "payment_status", "paid_at", "telegram_charge_id", "provider_charge_id",
                       "delivery_fee", "map_link")
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]
    actions = ["accept_orders", "cancel_orders"]
    list_per_page = 50

    @admin.display(description=_("Номер"), ordering="id")
    def number(self, obj):
        return obj.number

    @admin.display(description=_("Куда"))
    def place(self, obj):
        return _place(obj)

    @admin.display(description=_("На карте"))
    def map_link(self, obj):
        return _map_link(obj) or "—"

    @admin.display(description="", ordering="status")
    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, "#6b7280")
        return format_html(
            '<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{}" title="{}"></span>',
            color,
            obj.get_status_display(),
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Назначать можно только активных курьеров
        if db_field.name == "courier":
            kwargs["queryset"] = Courier.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Назначили курьера готовому заказу — значит, он передан курьеру
        if obj.courier_id and "courier" in form.changed_data and obj.status == Order.Status.READY:
            obj.status = Order.Status.HANDED_TO_COURIER
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Сумма заказа пересчитывается по позициям, если они есть
        if form.instance.items.exists():
            form.instance.recalculate_total()

    def _set_status(self, request, queryset, status, allowed_from):
        updated = queryset.filter(status__in=allowed_from).update(status=status, updated_at=timezone.now())
        skipped = queryset.count() - updated
        self.message_user(request, _("Обновлено заказов: %(n)s.") % {"n": updated})
        if skipped:
            self.message_user(request, _("Пропущено (неподходящий статус): %(n)s.") % {"n": skipped}, messages.WARNING)

    @admin.action(description=_("Принять выбранные заказы"), permissions=["change"])
    def accept_orders(self, request, queryset):
        self._set_status(request, queryset, Order.Status.ACCEPTED, [Order.Status.NEW])

    @admin.action(description=_("Отменить выбранные заказы"), permissions=["change"])
    def cancel_orders(self, request, queryset):
        not_final = [s for s in Order.Status.values if s not in Order.FINAL_STATUSES]
        self._set_status(request, queryset, Order.Status.CANCELLED, not_final)

    def get_urls(self):
        custom = [
            path(
                "statistics/",
                self.admin_site.admin_view(statistics_view(self.admin_site)),
                name="delivery_order_statistics",
            ),
        ]
        return custom + super().get_urls()

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["can_view_statistics"] = request.user.has_perm("delivery.view_statistics")
        return super().changelist_view(request, extra_context)


class KitchenStatusFilter(admin.SimpleListFilter):
    """Фильтр кухни — только её статусы."""

    title = _("Статус")
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return [(s.value, s.label) for s in Order.KITCHEN_STATUSES]

    def queryset(self, request, queryset):
        return queryset.filter(status=self.value()) if self.value() else queryset


@admin.register(KitchenOrder)
class KitchenOrderAdmin(admin.ModelAdmin):
    """Кухня видит заказы от «Принят» до «Готов» и меняет только статус — по одному или кнопками."""

    list_display = ("number", "created_at", "dishes", "comment", "status_badge", "status")
    list_display_links = None
    list_editable = ("status",)
    list_filter = (KitchenStatusFilter,)
    ordering = ("created_at",)  # первым — тот, кто ждёт дольше
    actions = ["start_cooking", "start_packing", "mark_ready"]
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).filter(status__in=Order.KITCHEN_STATUSES).prefetch_related("items__product")

    @admin.display(description=_("Номер"), ordering="id")
    def number(self, obj):
        return obj.number

    @admin.display(description=_("Блюда"))
    def dishes(self, obj):
        return ", ".join(f"{item.product.name} × {item.quantity}" for item in obj.items.all())

    @admin.display(description="", ordering="status")
    def status_badge(self, obj):
        return OrderAdmin.status_badge(self, obj)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        # В выпадающем списке — только кухонные статусы
        if db_field.name == "status":
            kwargs["choices"] = [(s.value, s.label) for s in Order.KITCHEN_STATUSES]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _move(self, request, queryset, status, allowed_from):
        OrderAdmin._set_status(self, request, queryset, status, allowed_from)

    @admin.action(description=_("Начать готовить"), permissions=["change"])
    def start_cooking(self, request, queryset):
        self._move(request, queryset, Order.Status.COOKING, [Order.Status.ACCEPTED])

    @admin.action(description=_("Упаковать"), permissions=["change"])
    def start_packing(self, request, queryset):
        self._move(request, queryset, Order.Status.PACKING, [Order.Status.COOKING])

    @admin.action(description=_("Готово"), permissions=["change"])
    def mark_ready(self, request, queryset):
        self._move(request, queryset, Order.Status.READY, [Order.Status.COOKING, Order.Status.PACKING])


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "telegram_id", "language", "registered_at")
    search_fields = ("name", "phone", "telegram_id")
    list_filter = ("language",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "name_kk", "name_en", "sort_order")
    list_editable = ("sort_order",)
    fieldsets = (
        (None, {"fields": ("name", "sort_order")}),
        (_("Переводы для бота"), {"fields": ("name_kk", "name_en")}),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "name_kk", "name_en", "category", "price", "is_available")
    list_filter = ("category", "is_available")
    list_editable = ("price", "is_available")
    search_fields = ("name", "name_kk", "name_en")
    fieldsets = (
        (None, {"fields": ("name", "description", "category", "price", "is_available")}),
        (
            _("Переводы для бота"),
            {"fields": ("name_kk", "description_kk", "name_en", "description_en")},
        ),
    )


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "telegram_id", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "phone")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "language")
    list_filter = ("language",)
