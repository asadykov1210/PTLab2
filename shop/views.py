from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Customer, CartItem


def get_customer():
    customer, _ = Customer.objects.get_or_create(name="TestUser")
    return customer


def index(request):
    products = Product.objects.all()
    customer = get_customer()
    discount = int(customer.get_discount() * 100)

    discount_info = [
        {"limit": 5, "percent": 5},
        {"limit": 10, "percent": 10},
        {"limit": 20, "percent": 15},
    ]

    return render(request, "shop/index.html", {
        "products": products,
        "discount": discount,
        "purchases": customer.purchases_count,
        "discount_info": discount_info,
    })


def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    customer = get_customer()

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        return render(request, "shop/confirm.html", {
            "product": product,
            "quantity": quantity,
        })

    return render(request, "shop/add_to_cart.html", {
        "product": product,
    })


def confirm_add(request, id):
    product = get_object_or_404(Product, id=id)
    customer = get_customer()
    quantity = int(request.GET.get("quantity", 1))

    CartItem.objects.create(customer=customer, product=product, quantity=quantity)
    customer.purchases_count += quantity
    customer.save()

    return redirect("cart")


def cart_view(request):
    customer = get_customer()
    items = CartItem.objects.filter(customer=customer)
    total = sum(item.get_total_price() for item in items)
    discount = int(customer.get_discount() * 100)

    return render(request, "shop/cart.html", {
        "items": items,
        "total": total,
        "discount": discount,
        "purchases": customer.purchases_count,
    })


def remove_from_cart(request, item_id):
    customer = get_customer()
    item = get_object_or_404(CartItem, id=item_id, customer=customer)

    customer.purchases_count -= item.quantity
    if customer.purchases_count < 0:
        customer.purchases_count = 0
    customer.save()

    item.delete()
    return redirect("cart")
