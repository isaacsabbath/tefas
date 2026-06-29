from django.contrib import admin

from .models import Order, OrderItem, PickupLocation


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0
	can_delete = False
	readonly_fields = ("product", "quantity", "price_at_purchase")
	fields = readonly_fields


@admin.register(PickupLocation)
class PickupLocationAdmin(admin.ModelAdmin):
	list_display = ("name", "address", "is_active")
	list_filter = ("is_active",)
	search_fields = ("name", "address")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "status", "payment_status", "total_amount", "created_at")
	list_filter = ("status", "payment_status", "delivery_method")
	search_fields = ("user__username", "user__email", "order_number", "mpesa_receipt_number")
	inlines = [OrderItemInline]
	actions = ["mark_as_delivered"]

	def get_readonly_fields(self, request, obj=None):
		return (
			"order_number",
			"user",
			"delivery_method",
			"delivery_address",
			"pickup_location",
			"phone_number",
			"total_amount",
			"mpesa_checkout_request_id",
			"mpesa_receipt_number",
			"payment_status",
			"status",
			"created_at",
			"updated_at",
		)

	def mark_as_delivered(self, request, queryset):
		queryset.update(status=Order.Status.DELIVERED)

	mark_as_delivered.short_description = "Mark selected orders as delivered"


admin.site.site_header = "Tefas Pharmacy Admin"

# Register your models here.
