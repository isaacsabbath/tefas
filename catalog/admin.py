from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("name", "slug")
	prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("name", "category", "price", "stock_quantity", "is_active")
	list_filter = ("category", "is_active")
	search_fields = ("name",)
	prepopulated_fields = {"slug": ("name",)}
	readonly_fields = ("image_preview",)

	def image_preview(self, obj):
		if obj.image:
			return format_html('<img src="{}" style="max-height: 120px; max-width: 120px; object-fit: cover;" />', obj.image.url)
		return "No image"

	image_preview.short_description = "Image preview"

# Register your models here.
