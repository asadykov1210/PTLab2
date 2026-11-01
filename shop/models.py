from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


class Product(models.Model):
    name = models.CharField("Наименование", max_length=200)
    price = models.PositiveIntegerField("Цена, руб.")

    def __str__(self):
        return self.name


class Customer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        null=True,
        blank=True,
    )
    name = models.CharField("Имя покупателя", max_length=100)
    purchases_count = models.IntegerField("Количество покупок", default=0)

    def update_purchases_count(self):
        """Пересчитывает количество купленных единиц по истории Purchase."""
        total = self.purchase_set.aggregate(total=Sum("quantity"))["total"] or 0
        self.purchases_count = total
        self.save(update_fields=["purchases_count"])

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
        """Цена в корзине. Скидка здесь НЕ применяется — она будет при оформлении."""
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity} ({self.customer.name})"


class Purchase(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Покупатель")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField("Количество", default=1)
    created_at = models.DateTimeField("Дата покупки", auto_now_add=True)
    price_at_purchase = models.PositiveIntegerField("Цена на момент покупки")

    def total_with_discount(self):
        """Итоговая цена покупки с учётом скидки покупателя."""
        discount = self.customer.get_discount()
        return int(self.price_at_purchase * self.quantity * (1 - discount))

    def __str__(self):
        return f"{self.product.name} x {self.quantity} — {self.customer.name}"
