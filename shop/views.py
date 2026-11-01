from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Product, Customer, CartItem, Purchase


def get_customer(request):
    """Возвращает Customer текущего пользователя. Если нет — создаёт."""
    if not request.user.is_authenticated:
        return None
    customer, _ = Customer.objects.get_or_create(
        user=request.user,
        defaults={"name": request.user.username},
    )
    return customer


# ==========================================
# АВТОРИЗАЦИЯ И РЕГИСТРАЦИЯ
# ==========================================

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user=user, name=user.username)
            login(request, user)
            return redirect("index")
    else:
        form = UserCreationForm()
    return render(request, "shop/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get("next", "index")
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, "shop/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


# ==========================================
# ОСНОВНАЯ ЛОГИКА МАГАЗИНА
# ==========================================

@login_required
def index(request):
    products = Product.objects.all()
    customer = get_customer(request)
    discount = int(customer.get_discount() * 100) if customer else 0
    purchases = customer.purchases_count if customer else 0

    discount_info = [
        {"limit": 5, "percent": 5},
        {"limit": 10, "percent": 10},
        {"limit": 20, "percent": 15},
    ]

    return render(request, "shop/index.html", {
        "products": products,
        "discount": discount,
        "purchases": purchases,
        "discount_info": discount_info,
    })


@login_required
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        return render(request, "shop/confirm.html", {
            "product": product,
            "quantity": quantity,
        })
    return render(request, "shop/add_to_cart.html", {"product": product})


@login_required
def confirm_add(request, id):
    product = get_object_or_404(Product, id=id)
    customer = get_customer(request)
    quantity = int(request.GET.get("quantity", 1))
    CartItem.objects.create(customer=customer, product=product, quantity=quantity)
    # purchases_count здесь НЕ трогаем — скидка начнёт действовать только после checkout
    return redirect("cart")


@login_required
def cart_view(request):
    customer = get_customer(request)
    items = CartItem.objects.filter(customer=customer)
    total = sum(item.get_total_price() for item in items)
    discount = int(customer.get_discount() * 100)
    return render(request, "shop/cart.html", {
        "items": items,
        "total": total,
        "discount": discount,
        "purchases": customer.purchases_count,
    })


@login_required
def remove_from_cart(request, item_id):
    customer = get_customer(request)
    item = get_object_or_404(CartItem, id=item_id, customer=customer)
    item.delete()
    return redirect("cart")


@login_required
def checkout(request):
    """Оформление заказа: корзина → история покупок."""
    customer = get_customer(request)
    items = CartItem.objects.filter(customer=customer)
    if not items:
        return redirect("cart")

    for item in items:
        Purchase.objects.create(
            customer=customer,
            product=item.product,
            quantity=item.quantity,
            price_at_purchase=item.product.price,
        )
        item.delete()

    customer.update_purchases_count()
    return redirect("purchases")


@login_required
def purchases_view(request):
    customer = get_customer(request)
    purchases = Purchase.objects.filter(customer=customer).order_by("-created_at")
    total = sum(p.total_with_discount() for p in purchases)
    return render(request, "shop/purchases.html", {
        "purchases": purchases,
        "total": total,
        "discount": int(customer.get_discount() * 100),
    })
