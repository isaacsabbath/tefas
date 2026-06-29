from django.db import models
from django.urls import reverse


class Category(models.Model):
	name = models.CharField(max_length=120, unique=True)
	slug = models.SlugField(max_length=140, unique=True)

	class Meta:
		ordering = ["name"]

	def __str__(self) -> str:
		return self.name


class Product(models.Model):
	category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
	name = models.CharField(max_length=180)
	slug = models.SlugField(max_length=200, unique=True)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	short_description = models.CharField(max_length=255)
	description = models.TextField()
	image = models.ImageField(upload_to="products/", blank=True, null=True)
	stock_quantity = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["name"]

	def __str__(self) -> str:
		return self.name

	def get_absolute_url(self):
		return reverse("catalog:product_detail", kwargs={"slug": self.slug})

	@property
	def in_stock(self) -> bool:
		return self.stock_quantity > 0

# Create your models here.
