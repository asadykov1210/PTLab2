from django.test import TestCase
from shop.models import Product, Customer, CartItem


class ProductModelTest(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create(name="Стол", price=2000)
        self.product2 = Product.objects.create(name="Стул", price=1000)

    def test_product_fields_types(self):
        self.assertIsInstance(self.product1.name, str)
        self.assertIsInstance(self.product1.price, int)
        self.assertIsInstance(self.product2.name, str)
        self.assertIsInstance(self.product2.price, int)

    def test_product_data_correctness(self):
        self.assertEqual(self.product1.price, 2000)
        self.assertEqual(self.product2.price, 1000)


class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="TestUser", purchases_count=0)

    def test_discount_none(self):
        self.assertEqual(self.customer.get_discount(), 0.0)

    def test_discount_5_percent(self):
        self.customer.purchases_count = 5
        self.assertEqual(self.customer.get_discount(), 0.05)

    def test_discount_10_percent(self):
        self.customer.purchases_count = 10
        self.assertEqual(self.customer.get_discount(), 0.10)

    def test_discount_15_percent(self):
        self.customer.purchases_count = 20
        self.assertEqual(self.customer.get_discount(), 0.15)


class CartItemModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="TestUser", purchases_count=10)
        self.product = Product.objects.create(name="Табурет", price=500)

    def test_total_price_with_discount(self):
        item = CartItem.objects.create(customer=self.customer, product=self.product, quantity=4)
        expected = int(500 * 4 * (1 - 0.10))
        self.assertEqual(item.get_total_price(), expected)

    def test_total_price_without_discount(self):
        self.customer.purchases_count = 0
        item = CartItem.objects.create(customer=self.customer, product=self.product, quantity=2)
        expected = 500 * 2
        self.assertEqual(item.get_total_price(), expected)
