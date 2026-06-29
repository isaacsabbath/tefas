from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
	fieldsets = BaseUserAdmin.fieldsets + (("Contact", {"fields": ("phone_number",)}),)
	add_fieldsets = BaseUserAdmin.add_fieldsets + (("Contact", {"fields": ("phone_number",)}),)
	list_display = ("username", "email", "phone_number", "is_staff", "is_active")
	search_fields = ("username", "email", "phone_number", "first_name", "last_name")

# Register your models here.
