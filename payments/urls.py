from django.urls import path

from .views import callback_view

app_name = "payments"

urlpatterns = [
    path("mpesa/callback/", callback_view, name="callback"),
]