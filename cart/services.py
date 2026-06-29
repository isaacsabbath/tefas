from django.db import transaction

from catalog.models import Product

from .models import Cart, CartItem


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def get_cart_count(user) -> int:
    if not user.is_authenticated:
        return 0
    return get_or_create_cart(user).item_count


@transaction.atomic
def add_product_to_cart(user, product: Product, quantity: int = 1) -> CartItem:
    cart = get_or_create_cart(user)
    quantity = max(1, quantity)
    item, created = CartItem.objects.select_for_update().get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity},
    )
    if not created:
        item.quantity += quantity
        item.save(update_fields=["quantity"])
    return item


@transaction.atomic
def update_cart_item_quantity(item: CartItem, quantity: int):
    if quantity <= 0:
        item.delete()
        return None
    item.quantity = quantity
    item.save(update_fields=["quantity"])
    return item