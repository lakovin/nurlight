"""Страница статистики для руководителя: /admin/delivery/order/statistics/"""
from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.db.models.functions import TruncDate
from django.template.response import TemplateResponse
from django.utils import timezone

from .models import Courier, Order, OrderItem

PERIODS = {
    "7": ("7 дней", 7),
    "30": ("30 дней", 30),
    "all": ("Всё время", None),
}
DEFAULT_PERIOD = "30"
# Сколько последних дней показывать на графике, если выбрано «Всё время»
CHART_DAYS_FOR_ALL = 30


def collect_statistics(days: int | None) -> dict:
    today = timezone.localdate()
    orders = Order.objects.all()
    if days:
        start = today - timedelta(days=days - 1)
        orders = orders.filter(created_at__date__gte=start)

    totals = orders.aggregate(
        count=Count("id"),
        delivered=Count("id", filter=Q(status=Order.Status.DELIVERED)),
        cancelled=Count("id", filter=Q(status=Order.Status.CANCELLED)),
        revenue=Sum("total", filter=Q(status=Order.Status.DELIVERED)),
    )
    revenue = totals["revenue"] or Decimal(0)
    count = totals["count"]
    in_progress = count - totals["delivered"] - totals["cancelled"]

    status_counts = dict(orders.values_list("status").annotate(n=Count("id")))
    by_status = [
        {
            "label": label,
            "code": code,
            "count": status_counts.get(code, 0),
            "percent": round(status_counts.get(code, 0) * 100 / count) if count else 0,
        }
        for code, label in Order.Status.choices
    ]

    chart_days = days or CHART_DAYS_FOR_ALL
    chart_start = today - timedelta(days=chart_days - 1)
    per_day = dict(
        Order.objects.filter(created_at__date__gte=chart_start)
        .annotate(day=TruncDate("created_at"))
        .values_list("day")
        .annotate(n=Count("id"))
    )
    daily = [
        {"day": chart_start + timedelta(days=i), "count": per_day.get(chart_start + timedelta(days=i), 0)}
        for i in range(chart_days)
    ]
    daily_max = max((d["count"] for d in daily), default=0)
    for d in daily:
        d["height"] = round(d["count"] * 100 / daily_max) if daily_max else 0

    line_total = ExpressionWrapper(F("price") * F("quantity"), output_field=DecimalField())
    top_products = (
        OrderItem.objects.filter(order__in=orders)
        .exclude(order__status=Order.Status.CANCELLED)
        .values("product__name")
        .annotate(units=Sum("quantity"), revenue=Sum(line_total))
        .order_by("-units")[:5]
    )

    period_filter = Q(orders__in=orders)
    couriers = (
        Courier.objects.annotate(
            delivered=Count("orders", filter=period_filter & Q(orders__status=Order.Status.DELIVERED)),
            active=Count(
                "orders",
                filter=period_filter
                & Q(orders__status__in=[Order.Status.HANDED_TO_COURIER, Order.Status.IN_TRANSIT]),
            ),
        )
        .filter(Q(is_active=True) | Q(delivered__gt=0))
        .order_by("-delivered", "name")
    )

    return {
        "count": count,
        "delivered": totals["delivered"],
        "cancelled": totals["cancelled"],
        "in_progress": in_progress,
        "revenue": revenue,
        "average_check": revenue / totals["delivered"] if totals["delivered"] else Decimal(0),
        "cancel_rate": round(totals["cancelled"] * 100 / count) if count else 0,
        "by_status": by_status,
        "daily": daily,
        "daily_max": daily_max,
        "top_products": list(top_products),
        "couriers": list(couriers),
    }


def statistics_view(admin_site):
    def view(request):
        if not request.user.has_perm("delivery.view_statistics"):
            raise PermissionDenied
        period = request.GET.get("period", DEFAULT_PERIOD)
        if period not in PERIODS:
            period = DEFAULT_PERIOD
        label, days = PERIODS[period]
        context = {
            **admin_site.each_context(request),
            "title": "Статистика",
            "period": period,
            "period_label": label,
            "periods": [(key, value[0]) for key, value in PERIODS.items()],
            "stats": collect_statistics(days),
            "opts": Order._meta,
        }
        return TemplateResponse(request, "admin/delivery/statistics.html", context)

    return view
