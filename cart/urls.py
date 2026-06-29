from django.urls import path

from .views import add_to_cart, cart_detail, remove_cart_item, update_cart_item

app_name = "cart"

urlpatterns = [
    path("", cart_detail, name="detail"),
    path("add/<int:product_id>/", add_to_cart, name="add"),
    path("items/<int:item_id>/update/", update_cart_item, name="item_update"),
    path("items/<int:item_id>/remove/", remove_cart_item, name="item_remove"),
]