from cart.services import get_cart_count


def cart_summary(request):
    return {"cart_count": get_cart_count(request.user) if hasattr(request, "user") else 0}