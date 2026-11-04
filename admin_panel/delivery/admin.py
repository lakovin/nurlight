from django.contrib import admin

from .models import FAQ, Category, Client, Courier, Order, OrderItem, Product


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "client", "status", "courier", "total", "created_at")
    list_filter = ("status", "courier", "created_at")
    list_editable = ("status", "courier")
    search_fields = ("id", "address", "client__name", "client__phone")
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]

    @admin.display(description="Номер", ordering="id")
    def number(self, obj):
        return obj.number


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


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "language")
    list_filter = ("language",)
