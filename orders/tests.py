from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from cart.models import Cart, CartItem
from catalog.models import Category, Product

from .services import create_order_from_cart

class OrdersTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(
			username="buyer@example.com",
			email="buyer@example.com",
			password="password12345",
			phone_number="254712345679",
		)
		category = Category.objects.create(name="Vitamins", slug="vitamins")
		self.product_a = Product.objects.create(
			category=category,
			name="Vitamin A",
			slug="vitamin-a",
			price=Decimal("100.00"),
			short_description="Boosts immunity",
			description="Daily vitamins.",
			stock_quantity=10,
			is_active=True,
		)
		self.product_b = Product.objects.create(
			category=category,
			name="Vitamin B",
			slug="vitamin-b",
			price=Decimal("150.00"),
			short_description="Energy support",
			description="Supports wellbeing.",
			stock_quantity=10,
			is_active=True,
		)
		self.cart = Cart.objects.create(user=self.user)
		CartItem.objects.create(cart=self.cart, product=self.product_a, quantity=2)
		CartItem.objects.create(cart=self.cart, product=self.product_b, quantity=1)

	def test_order_total_calculation_from_cart(self):
		order = create_order_from_cart(
			self.user,
			{
				"delivery_method": "home",
				"delivery_address": "Nairobi",
				"pickup_location": None,
				"phone_number": "254712345679",
			},
		)

		self.assertEqual(order.total_amount, Decimal("350.00"))
		self.assertEqual(order.items.count(), 2)
from django.test import TestCase

# Create your tests here.
