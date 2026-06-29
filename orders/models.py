import uuid

from django.conf import settings
from django.db import models


class PickupLocation(models.Model):
	name = models.CharField(max_length=150)
	address = models.CharField(max_length=255)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ["name"]

	def __str__(self) -> str:
		return f"{self.name} - {self.address}"


class Order(models.Model):
	class Status(models.TextChoices):
		PENDING = "pending", "Pending"
		PAID = "paid", "Paid"
		PROCESSING = "processing", "Processing"
		DELIVERED = "delivered", "Delivered"
		CANCELLED = "cancelled", "Cancelled"

	class DeliveryMethod(models.TextChoices):
		HOME = "home", "Home Delivery"
		PICKUP = "pickup", "Pickup"

	class PaymentStatus(models.TextChoices):
		UNPAID = "unpaid", "Unpaid"
		PAID = "paid", "Paid"
		FAILED = "failed", "Failed"

	order_number = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	delivery_method = models.CharField(max_length=20, choices=DeliveryMethod.choices)
	delivery_address = models.TextField(blank=True, null=True)
	pickup_location = models.ForeignKey(PickupLocation, on_delete=models.SET_NULL, blank=True, null=True, related_name="orders")
	phone_number = models.CharField(max_length=12)
	total_amount = models.DecimalField(max_digits=10, decimal_places=2)
	mpesa_checkout_request_id = models.CharField(max_length=120, blank=True, null=True)
	mpesa_receipt_number = models.CharField(max_length=120, blank=True, null=True)
	payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return f"Order {self.order_number}"


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
	product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT, related_name="order_items")
	quantity = models.PositiveIntegerField()
	price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

	class Meta:
		ordering = ["id"]

	def __str__(self) -> str:
		return f"{self.quantity} x {self.product}"

	@property
	def line_total(self):
		return self.quantity * self.price_at_purchase

# Create your models here.
