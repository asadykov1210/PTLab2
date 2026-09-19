from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add/<int:id>/", views.add_to_cart, name="add_to_cart"),
    path("confirm/<int:id>/", views.confirm_add, name="confirm_add"),
    path("cart/", views.cart_view, name="cart"),
    path("remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
]
