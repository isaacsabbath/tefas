from django.urls import path

from .views import checkout_view, confirmation_view, order_status_view, retry_payment_view

app_name = "orders"

urlpatterns = [
    path("checkout/", checkout_view, name="checkout"),
    path("<uuid:order_number>/confirmation/", confirmation_view, name="confirmation"),
    path("<uuid:order_number>/status/", order_status_view, name="status"),
    path("<uuid:order_number>/retry-payment/", retry_payment_view, name="retry_payment"),
]