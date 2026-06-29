from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product

from .models import Cart, CartItem

class CartTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(
			username="customer@example.com",
			email="customer@example.com",
			password="password12345",
			phone_number="254712345678",
		)
		category = Category.objects.create(name="Painkillers", slug="painkillers")
		self.product = Product.objects.create(
			category=category,
			name="Painkiller Tablets",
			slug="painkiller-tablets",
			price=Decimal("100.00"),
			short_description="Pain relief",
			description="Relieves pain and fever.",
			stock_quantity=10,
			is_active=True,
		)

	def test_add_update_and_remove_cart_item(self):
		self.client.force_login(self.user)

		add_response = self.client.post(
			reverse("cart:add", args=[self.product.id]),
			{"quantity": 2},
			HTTP_X_REQUESTED_WITH="XMLHttpRequest",
		)
		self.assertEqual(add_response.status_code, 200)
		self.assertEqual(add_response.json()["cart_count"], 2)

		cart = Cart.objects.get(user=self.user)
		item = CartItem.objects.get(cart=cart, product=self.product)
		self.assertEqual(item.quantity, 2)

		self.client.post(reverse("cart:item_update", args=[item.id]), {"quantity": 3})
		item.refresh_from_db()
		self.assertEqual(item.quantity, 3)

		self.client.post(reverse("cart:item_remove", args=[item.id]))
		self.assertFalse(CartItem.objects.filter(cart=cart).exists())
from django.test import TestCase

# Create your tests here.
