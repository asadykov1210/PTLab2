from django.contrib import admin
from .models import Product, Customer, CartItem, Purchase

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(CartItem)
admin.site.register(Purchase)