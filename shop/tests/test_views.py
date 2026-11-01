from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Product, Customer, CartItem, Purchase


class ViewTests(TestCase):
    """Тесты представлений: авторизация, корзина, оформление заказа."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.customer = Customer.objects.create(user=self.user, name="testuser")
        self.product = Product.objects.create(name="Стол", price=1000)

    def test_index_requires_login(self):
        response = self.client.get(reverse("index"))
        self.assertRedirects(response, f"/login/?next={reverse('index')}")

    def test_register_view(self):
        response = self.client.post(reverse("register"), {
            "username": "newuser",
            "password1": "complexpass123",
            "password2": "complexpass123",
        })
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertTrue(Customer.objects.filter(user__username="newuser").exists())

    def test_login_view(self):
        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "pass123",
        })
        self.assertRedirects(response, reverse("index"))

    def test_logout_view(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("login"))

    def test_cart_view_empty(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("cart"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Корзина пуста")

    def test_add_to_cart_get(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("add_to_cart", args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/add_to_cart.html")

    def test_confirm_add_creates_cart_item(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(
            reverse("confirm_add", args=[self.product.id]) + "?quantity=2"
        )
        self.assertRedirects(response, reverse("cart"))
        self.assertEqual(CartItem.objects.filter(customer=self.customer).count(), 1)
        item = CartItem.objects.first()
        self.assertEqual(item.quantity, 2)

    def test_remove_from_cart(self):
        self.client.login(username="testuser", password="pass123")
        item = CartItem.objects.create(customer=self.customer, product=self.product, quantity=1)
        response = self.client.post(reverse("remove_from_cart", args=[item.id]))
        self.assertRedirects(response, reverse("cart"))
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())

    def test_checkout_moves_to_purchases_and_updates_count(self):
        """Оформление заказа: корзина очищается, создаются Purchase, счётчик растёт."""
        self.client.login(username="testuser", password="pass123")
        CartItem.objects.create(customer=self.customer, product=self.product, quantity=2)

        response = self.client.post(reverse("checkout"))
        self.assertRedirects(response, reverse("purchases"))

        # Корзина пуста
        self.assertEqual(CartItem.objects.filter(customer=self.customer).count(), 0)
        # Покупка создана
        self.assertEqual(Purchase.objects.filter(customer=self.customer).count(), 1)
        # Счётчик покупок обновлён
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.purchases_count, 2)

    def test_customer_isolation(self):
        """Каждый пользователь видит только свою корзину."""
        other_user = User.objects.create_user(username="other", password="pass123")
        other_customer = Customer.objects.create(user=other_user, name="other")

        # Корзина первого пользователя (testuser) - 1 товар
        CartItem.objects.create(customer=self.customer, product=self.product, quantity=1)
        # Корзина второго пользователя (other) - 3 товара
        CartItem.objects.create(customer=other_customer, product=self.product, quantity=3)

        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("cart"))
        
        # Проверяем, что на странице есть ячейка с количеством 1 (наш товар)
        self.assertContains(response, "<td>1</td>", html=True)
        # Проверяем, что на странице НЕТ ячейки с количеством 3 (чужой товар)
        self.assertNotContains(response, "<td>3</td>", html=True)