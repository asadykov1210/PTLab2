from django.test import TestCase, Client
from django.urls import reverse
from shop.models import Product, Customer, CartItem


class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(name="TestUser", purchases_count=6)
        Product.objects.create(name="Стол", price=2000)
        Product.objects.create(name="Стул", price=1000)

    def test_index_page_accessible(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Магазин товаров для быта")

    def test_discount_displayed(self):
        response = self.client.get(reverse("index"))
        self.assertContains(response, "Текущая скидка: 5%")


class AddToCartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(name="TestUser", purchases_count=0)
        self.product = Product.objects.create(name="Стол", price=2000)

    def test_add_to_cart_form_display(self):
        response = self.client.get(reverse("add_to_cart", args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Количество")

    def test_confirm_page_display(self):
        response = self.client.post(reverse("add_to_cart", args=[self.product.id]), {"quantity": 3})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Вы хотите купить")

    def test_confirm_add_creates_item(self):
        response = self.client.get(reverse("confirm_add", args=[self.product.id]), {"quantity": 2})
        self.assertEqual(CartItem.objects.count(), 1)
        item = CartItem.objects.first()
        self.assertEqual(item.quantity, 2)


class CartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(name="TestUser", purchases_count=10)
        self.product1 = Product.objects.create(name="Стул", price=1000)
        self.product2 = Product.objects.create(name="Табурет", price=500)
        CartItem.objects.create(customer=self.customer, product=self.product1, quantity=2)
        CartItem.objects.create(customer=self.customer, product=self.product2, quantity=4)

    def test_cart_page_accessible(self):
        response = self.client.get(reverse("cart"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Корзина")

    def test_cart_total_sum(self):
        response = self.client.get(reverse("cart"))
        total_expected = int(1000 * 2 * (1 - 0.10)) + int(500 * 4 * (1 - 0.10))
        self.assertContains(response, str(total_expected))


class RemoveFromCartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(name="TestUser", purchases_count=5)
        self.product = Product.objects.create(name="Стул", price=1000)
        self.item = CartItem.objects.create(customer=self.customer, product=self.product, quantity=3)

    def test_remove_item(self):
        response = self.client.post(reverse("remove_from_cart", args=[self.item.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_purchases_count_updated(self):
        self.client.post(reverse("remove_from_cart", args=[self.item.id]))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.purchases_count, 2)
