from decimal import Decimal

from django.db import transaction

from cart.services import get_or_create_cart

from .models import Order, OrderItem


@transaction.atomic
def create_order_from_cart(user, cleaned_data) -> Order:
    cart = get_or_create_cart(user)
    items = list(cart.items.select_related("product"))
    if not items:
        raise ValueError("Cart is empty.")

    total_amount = sum((item.quantity * item.product.price for item in items), Decimal("0.00"))
    order = Order.objects.create(
        user=user,
        delivery_method=cleaned_data["delivery_method"],
        delivery_address=cleaned_data.get("delivery_address") or None,
        pickup_location=cleaned_data.get("pickup_location"),
        phone_number=cleaned_data["phone_number"],
        total_amount=total_amount,
    )
    OrderItem.objects.bulk_create(
        [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price,
            )
            for item in items
        ]
    )
    return order