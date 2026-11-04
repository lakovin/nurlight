from django.contrib import admin, messages
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html

from .models import FAQ, Category, Client, Courier, Order, OrderItem, Product
from .statistics import statistics_view

STATUS_COLORS = {
    Order.Status.NEW: "#d97706",
    Order.Status.ACCEPTED: "#2563eb",
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
    list_display = ("number", "created_at", "client", "address", "total", "status_badge", "status", "courier")
    list_display_links = ("number",)
    list_filter = ("status", "courier", "created_at")
    list_editable = ("status", "courier")
    list_select_related = ("client", "courier")
    search_fields = ("id", "address", "client__name", "client__phone")
    autocomplete_fields = ("client",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]
    actions = ["accept_orders", "cancel_orders"]
    list_per_page = 50

    @admin.display(description="Номер", ordering="id")
    def number(self, obj):
        return obj.number

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
        # Назначили курьера новому или принятому заказу — значит, он передан курьеру
        if obj.courier_id and "courier" in form.changed_data and obj.status in (
            Order.Status.NEW,
            Order.Status.ACCEPTED,
        ):
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
        self.message_user(request, f"Обновлено заказов: {updated}.")
        if skipped:
            self.message_user(request, f"Пропущено (неподходящий статус): {skipped}.", messages.WARNING)

    @admin.action(description="Принять выбранные заказы", permissions=["change"])
    def accept_orders(self, request, queryset):
        self._set_status(request, queryset, Order.Status.ACCEPTED, [Order.Status.NEW])

    @admin.action(description="Отменить выбранные заказы", permissions=["change"])
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


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "telegram_id", "language", "registered_at")
    search_fields = ("name", "phone", "telegram_id")
    list_filter = ("language",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order")
    list_editable = ("sort_order",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_available")
    list_filter = ("category", "is_available")
    list_editable = ("price", "is_available")
    search_fields = ("name",)


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "telegram_id", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "phone")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "language")
    list_filter = ("language",)
