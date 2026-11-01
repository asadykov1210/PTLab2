from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Product, Customer, CartItem, Purchase


class ModelTests(TestCase):
    """Тесты моделей: Product, Customer, CartItem, Purchase."""

    def setUp(self):
        self.product = Product.objects.create(name="Стол", price=1000)
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.customer = Customer.objects.create(user=self.user, name="testuser")

    def test_product_str(self):
        self.assertEqual(str(self.product), "Стол")

    def test_customer_str(self):
        self.assertEqual(str(self.customer), "testuser")

    def test_get_discount_zero(self):
        self.assertEqual(self.customer.get_discount(), 0.0)

    def test_get_discount_5_percent(self):
        self.customer.purchases_count = 5
        self.assertEqual(self.customer.get_discount(), 0.05)

    def test_get_discount_10_percent(self):
        self.customer.purchases_count = 10
        self.assertEqual(self.customer.get_discount(), 0.10)

    def test_get_discount_15_percent(self):
        self.customer.purchases_count = 20
        self.assertEqual(self.customer.get_discount(), 0.15)

    def test_update_purchases_count(self):
        """purchases_count должен пересчитываться по фактическим покупкам."""
        Purchase.objects.create(
            customer=self.customer, product=self.product,
            quantity=3, price_at_purchase=1000
        )
        Purchase.objects.create(
            customer=self.customer, product=self.product,
            quantity=2, price_at_purchase=1000
        )
        self.customer.update_purchases_count()
        self.assertEqual(self.customer.purchases_count, 5)

    def test_cart_item_total_price_no_discount(self):
        """В корзине цена всегда без скидки."""
        self.customer.purchases_count = 20  # даже при большой скидке
        item = CartItem.objects.create(customer=self.customer, product=self.product, quantity=2)
        self.assertEqual(item.get_total_price(), 2000)

    def test_purchase_total_with_discount(self):
        self.customer.purchases_count = 10  # скидка 10%
        purchase = Purchase.objects.create(
            customer=self.customer, product=self.product,
            quantity=2, price_at_purchase=1000
        )
        # 1000 * 2 * 0.9 = 1800
        self.assertEqual(purchase.total_with_discount(), 1800)