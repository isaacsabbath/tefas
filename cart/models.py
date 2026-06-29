from decimal import Decimal

from django.conf import settings
from django.db import models


class Cart(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"Cart for {self.user}"

	@property
	def item_count(self) -> int:
		return sum(item.quantity for item in self.items.select_related("product"))

	@property
	def total_amount(self):
		return sum((item.line_total for item in self.items.select_related("product")), Decimal("0.00"))


class CartItem(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
	product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="cart_items")
	quantity = models.PositiveIntegerField(default=1)

	class Meta:
		unique_together = ("cart", "product")
		ordering = ["product__name"]

	def __str__(self) -> str:
		return f"{self.quantity} x {self.product}"

	@property
	def line_total(self):
		return self.quantity * self.product.price

# Create your models here.
