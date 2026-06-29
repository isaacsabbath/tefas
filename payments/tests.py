from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from catalog.models import Category, Product
from orders.models import Order

from .mpesa import initiate_stk_push

class PaymentsTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(
			username="mpesa@example.com",
			email="mpesa@example.com",
			password="password12345",
			phone_number="254712345680",
		)
		category = Category.objects.create(name="First Aid", slug="first-aid")
		self.product = Product.objects.create(
			category=category,
			name="Bandages",
			slug="bandages",
			price=Decimal("100.00"),
			short_description="Wound care",
			description="For minor wound dressing.",
			stock_quantity=10,
			is_active=True,
		)
		self.order = Order.objects.create(
			user=self.user,
			status=Order.Status.PENDING,
			delivery_method=Order.DeliveryMethod.HOME,
			delivery_address="Nairobi",
			phone_number="254712345680",
			total_amount=Decimal("100.00"),
		)

	@patch("payments.mpesa.requests.post")
	@patch("payments.mpesa.get_access_token", return_value="mock-token")
	def test_initiate_stk_push_triggers_request(self, mock_token, mock_post):
		response = Mock()
		response.status_code = 200
		response.json.return_value = {
			"ResponseCode": "0",
			"ResponseDescription": "Success",
			"CheckoutRequestID": "ws_CO_123",
		}
		mock_post.return_value = response

		payload = initiate_stk_push(self.order)

		self.assertEqual(payload["CheckoutRequestID"], "ws_CO_123")
		mock_token.assert_called_once()
		mock_post.assert_called_once()
from django.test import TestCase

# Create your tests here.
