from django.db import models


class Product(models.Model):
    name = models.CharField("Наименование", max_length=200)
    price = models.PositiveIntegerField("Цена, руб.")

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField("Имя покупателя", max_length=100)
    purchases_count = models.IntegerField("Количество покупок", default=0)

    def get_discount(self):
        if self.purchases_count >= 20:
            return 0.15
        elif self.purchases_count >= 10:
            return 0.10
        elif self.purchases_count >= 5:
            return 0.05
        return 0.0

    def __str__(self):
        return self.name


class CartItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Покупатель")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField("Количество", default=1)

    def get_total_price(self):
        discount = self.customer.get_discount()
        return int(self.product.price * self.quantity * (1 - discount))

    def __str__(self):
        return f"{self.product.name} x {self.quantity} ({self.customer.name})"
