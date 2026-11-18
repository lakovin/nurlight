import json

from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from delivery.models import FAQ, Category, Client, Order, OrderItem, Product

from . import assistant
from .cart import Cart
from .forms import CheckoutForm, OrderLookupForm
from .phones import normalize_phone

MY_ORDERS_KEY = "my_orders"
# Путь заказа, который видит клиент; «Отменён» показывается отдельно
FLOW = [
    Order.Status.NEW,
    Order.Status.ACCEPTED,
    Order.Status.HANDED_TO_COURIER,
    Order.Status.IN_TRANSIT,
    Order.Status.DELIVERED,
]
STEP_HINTS = {
    Order.Status.NEW: "Заказ оформлен",
    Order.Status.ACCEPTED: "Оператор подтвердил заказ",
    Order.Status.HANDED_TO_COURIER: "Курьер забрал заказ",
    Order.Status.IN_TRANSIT: "Курьер едет к вам",
    Order.Status.DELIVERED: "Заказ у вас. Приятного аппетита!",
}


def _categories():
    available = Q(products__is_available=True)
    return Category.objects.annotate(product_count=Count("products", filter=available)).filter(product_count__gt=0)


def home(request):
    top_ids = list(
        OrderItem.objects.filter(product__is_available=True)
        .values("product")
        .annotate(units=Sum("quantity"))
        .order_by("-units")
        .values_list("product", flat=True)[:4]
    )
    popular = sorted(Product.objects.filter(pk__in=top_ids).select_related("category"), key=lambda p: top_ids.index(p.pk))
    if len(popular) < 4:
        popular += list(Product.objects.filter(is_available=True).exclude(pk__in=top_ids).select_related("category")[: 4 - len(popular)])
    return render(request, "shop/home.html", {
        "categories": _categories(),
        "popular": popular,
        "faqs": FAQ.objects.filter(language="ru"),
    })


def catalog(request):
    categories = _categories()
    products = Product.objects.filter(is_available=True).select_related("category")
    current = None
    if category_id := request.GET.get("category"):
        current = next((c for c in categories if str(c.pk) == category_id), None)
        if current is None:
            raise Http404("Нет такой категории")
        products = products.filter(category=current)
    query = request.GET.get("q", "").strip()
    if query:
        # Ищем в Python: SQLite без учёта регистра сравнивает только латиницу, а меню на кириллице
        needle = query.casefold()
        products = [p for p in products if needle in f"{p.name} {p.description}".casefold()]
    return render(request, "shop/catalog.html", {
        "categories": categories,
        "current": current,
        "products": products,
        "query": query,
        "total_count": sum(c.product_count for c in categories),
    })


def _back(request, fallback="shop:catalog"):
    target = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(target)
    return redirect(fallback)


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_available=True)
    Cart(request).change(product.pk, 1)
    messages.success(request, f"«{product.name}» в корзине")
    return _back(request)


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    action = request.POST.get("action")
    if action == "inc":
        cart.change(product_id, 1)
    elif action == "dec":
        cart.change(product_id, -1)
    elif action == "remove":
        cart.remove(product_id)
    return redirect("shop:checkout")


@transaction.atomic
def _place_order(lines, data) -> Order:
    # Один телефон — один клиент: заказы с сайта и из бота сходятся в одной карточке клиента
    client = Client.objects.filter(phone=data["phone"]).order_by("pk").first()
    if client is None:
        client = Client.objects.create(name=data["name"], phone=data["phone"])
    order = Order.objects.create(client=client, address=data["address"], comment=data["comment"])
    OrderItem.objects.bulk_create(
        OrderItem(order=order, product=line.product, quantity=line.quantity, price=line.product.price)
        for line in lines
    )
    order.recalculate_total()
    return order


def _remember_order(request, order):
    mine = request.session.get(MY_ORDERS_KEY, [])
    if order.pk not in mine:
        request.session[MY_ORDERS_KEY] = (mine + [order.pk])[-20:]


def checkout(request):
    cart = Cart(request)
    lines = cart.lines()
    form = CheckoutForm(request.POST or None)
    if request.method == "POST":
        if not lines:
            messages.error(request, "Корзина пуста — добавьте что-нибудь из меню")
            return redirect("shop:catalog")
        if form.is_valid():
            order = _place_order(lines, form.cleaned_data)
            cart.clear()
            _remember_order(request, order)
            return redirect("shop:order_status", pk=order.pk)
    return render(request, "shop/checkout.html", {
        "lines": lines,
        "total": cart.total(lines),
        "items_count": sum(line.quantity for line in lines),
        "form": form,
    })


def order_lookup(request):
    form = OrderLookupForm(request.GET or None)
    if request.GET and form.is_valid():
        order = Order.objects.select_related("client").filter(pk=form.cleaned_data["number"]).first()
        if order and normalize_phone(order.client.phone) == form.cleaned_data["phone"]:
            _remember_order(request, order)
            return redirect("shop:order_status", pk=order.pk)
        form.add_error(None, "Заказ не найден. Проверьте номер и телефон, который указывали при заказе.")
    return render(request, "shop/order_lookup.html", {"form": form})


def order_status(request, pk):
    # Чужой заказ не показываем: только оформленный в этом браузере или найденный по номеру и телефону
    if pk not in request.session.get(MY_ORDERS_KEY, []):
        return redirect("shop:order_lookup")
    order = get_object_or_404(Order.objects.select_related("courier").prefetch_related("items__product"), pk=pk)
    steps = []
    if order.status != Order.Status.CANCELLED:
        current = FLOW.index(order.status)
        for i, status in enumerate(FLOW):
            if i < current or order.status == Order.Status.DELIVERED:
                state = "done"
            elif i == current:
                state = "current"
            else:
                state = "todo"
            steps.append({"label": status.label, "hint": STEP_HINTS[status] if state != "todo" else "", "state": state})
    show_courier = order.courier and order.status in (Order.Status.HANDED_TO_COURIER, Order.Status.IN_TRANSIT)
    return render(request, "shop/order_status.html", {"order": order, "steps": steps, "show_courier": show_courier})


@require_POST
def assistant_chat(request):
    """Окно AI-консультанта: {"message": "..."} → {"answer": "...", "ok": true}; {"action": "clear"} — новый диалог."""
    try:
        data = json.loads(request.body or b"{}")
    except ValueError:
        return JsonResponse({"error": "Неверный запрос"}, status=400)
    if data.get("action") == "clear":
        assistant.clear(request.session)
        return JsonResponse({"ok": True})
    question = str(data.get("message", "")).strip()
    if not question:
        return JsonResponse({"error": "Напишите вопрос"}, status=400)
    if len(question) > assistant.MAX_QUESTION:
        return JsonResponse({"error": f"Вопрос длиннее {assistant.MAX_QUESTION} символов"}, status=400)
    if assistant.rate_limited(request.session):
        return JsonResponse({"error": "Слишком много вопросов подряд. Попробуйте через несколько минут."}, status=429)
    answer, ok = assistant.ask(request.session, question)
    return JsonResponse({"answer": answer, "ok": ok})
