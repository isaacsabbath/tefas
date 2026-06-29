from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Product

from .models import CartItem
from .services import add_product_to_cart, get_or_create_cart, update_cart_item_quantity


def _json_or_redirect(request, payload, status=200):
	wants_json = request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("accept", "")
	if wants_json:
		return JsonResponse(payload, status=status)
	return redirect(request.META.get("HTTP_REFERER") or payload.get("redirect_url") or "cart:detail")


@login_required
def cart_detail(request):
	cart = get_or_create_cart(request.user)
	return render(request, "cart/cart_detail.html", {"cart": cart, "items": cart.items.select_related("product", "product__category")})


@login_required
def add_to_cart(request, product_id):
	if request.method != "POST":
		return HttpResponseBadRequest("POST required")
	product = get_object_or_404(Product, pk=product_id, is_active=True)
	quantity = int(request.POST.get("quantity", 1) or 1)
	quantity = max(1, min(quantity, product.stock_quantity or quantity))
	item = add_product_to_cart(request.user, product, quantity)
	cart = get_or_create_cart(request.user)
	return _json_or_redirect(
		request,
		{
			"ok": True,
			"cart_count": cart.item_count,
			"item_quantity": item.quantity,
			"message": f"Added {product.name} to cart.",
		},
	)


@login_required
def update_cart_item(request, item_id):
	if request.method != "POST":
		return HttpResponseBadRequest("POST required")
	cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
	quantity = int(request.POST.get("quantity", cart_item.quantity) or 0)
	update_cart_item_quantity(cart_item, quantity)
	messages.success(request, "Cart updated.")
	return redirect("cart:detail")


@login_required
def remove_cart_item(request, item_id):
	if request.method != "POST":
		return HttpResponseBadRequest("POST required")
	cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
	cart_item.delete()
	messages.success(request, "Item removed from cart.")
	return redirect("cart:detail")

# Create your views here.
