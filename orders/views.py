from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from cart.services import get_or_create_cart
from payments.mpesa import MpesaApiError, MpesaNetworkError, initiate_stk_push

from .forms import CheckoutForm
from .models import Order
from .services import create_order_from_cart


def _pending_order_from_session(request):
	order_number = request.session.get("pending_order_number")
	if not order_number:
		return None
	try:
		return Order.objects.select_related("pickup_location", "user").get(order_number=order_number, user=request.user)
	except Order.DoesNotExist:
		return None


@login_required
def checkout_view(request):
	cart = get_or_create_cart(request.user)
	cart_items = cart.items.select_related("product", "product__category")
	if not cart_items.exists():
		messages.info(request, "Your cart is empty.")
		return redirect("core:home")

	pending_order = _pending_order_from_session(request)
	if pending_order and pending_order.payment_status == Order.PaymentStatus.PAID:
		return redirect("orders:confirmation", order_number=pending_order.order_number)
	if request.method == "POST":
		form = CheckoutForm(request.POST)
		if form.is_valid():
			order = pending_order or create_order_from_cart(request.user, form.cleaned_data)
			if pending_order:
				order.delivery_method = form.cleaned_data["delivery_method"]
				order.delivery_address = form.cleaned_data.get("delivery_address") or None
				order.pickup_location = form.cleaned_data.get("pickup_location")
				order.phone_number = form.cleaned_data["phone_number"]
				order.save(update_fields=["delivery_method", "delivery_address", "pickup_location", "phone_number", "updated_at"])
			try:
				mpesa_response = initiate_stk_push(order)
			except (MpesaNetworkError, MpesaApiError) as exc:
				order.payment_status = Order.PaymentStatus.FAILED
				order.save(update_fields=["payment_status", "updated_at"])
				request.session["pending_order_number"] = str(order.order_number)
				return render(
					request,
					"orders/checkout.html",
					{
						"cart": cart,
						"items": cart_items,
						"form": form,
						"pending_order": order,
						"payment_error": str(exc),
						"waiting_for_payment": False,
					},
				)

			order.mpesa_checkout_request_id = mpesa_response.get("CheckoutRequestID")
			order.payment_status = Order.PaymentStatus.UNPAID
			order.status = Order.Status.PENDING
			order.save(update_fields=["mpesa_checkout_request_id", "payment_status", "status", "updated_at"])
			request.session["pending_order_number"] = str(order.order_number)
			return render(
				request,
				"orders/checkout.html",
				{
					"cart": cart,
					"items": cart_items,
					"form": form,
					"pending_order": order,
					"waiting_for_payment": True,
				},
			)
	else:
		initial = {"phone_number": request.user.phone_number}
		if pending_order:
			initial.update(
				{
					"delivery_method": pending_order.delivery_method,
					"delivery_address": pending_order.delivery_address,
					"pickup_location": pending_order.pickup_location,
					"phone_number": pending_order.phone_number,
				}
			)
		form = CheckoutForm(initial=initial)

	return render(
		request,
		"orders/checkout.html",
		{
			"cart": cart,
			"items": cart_items,
			"form": form,
			"pending_order": pending_order,
			"waiting_for_payment": bool(pending_order and pending_order.payment_status != Order.PaymentStatus.FAILED),
		},
	)


@login_required
def retry_payment_view(request, order_number):
	order = get_object_or_404(Order, order_number=order_number, user=request.user)
	if request.method != "POST":
		return HttpResponseBadRequest("POST required")
	try:
		response = initiate_stk_push(order)
		order.mpesa_checkout_request_id = response.get("CheckoutRequestID")
		order.payment_status = Order.PaymentStatus.UNPAID
		order.save(update_fields=["mpesa_checkout_request_id", "payment_status", "updated_at"])
		messages.success(request, "STK push sent again. Check your phone.")
	except (MpesaNetworkError, MpesaApiError) as exc:
		order.payment_status = Order.PaymentStatus.FAILED
		order.save(update_fields=["payment_status", "updated_at"])
		messages.error(request, f"Payment retry failed: {exc}")
	request.session["pending_order_number"] = str(order.order_number)
	return redirect("orders:checkout")


@login_required
def order_status_view(request, order_number):
	order = get_object_or_404(Order, order_number=order_number, user=request.user)
	return JsonResponse(
		{
			"order_number": str(order.order_number),
			"payment_status": order.payment_status,
			"status": order.status,
			"redirect_url": reverse("orders:confirmation", kwargs={"order_number": order.order_number}) if order.payment_status == Order.PaymentStatus.PAID else None,
		}
	)


@login_required
def confirmation_view(request, order_number):
	order = get_object_or_404(Order.objects.select_related("pickup_location", "user").prefetch_related("items__product"), order_number=order_number, user=request.user)
	if order.payment_status != Order.PaymentStatus.PAID:
		messages.info(request, "That order has not been paid yet.")
		return redirect("orders:checkout")

	cart = get_or_create_cart(request.user)
	cart.items.all().delete()
	request.session.pop("pending_order_number", None)
	return render(request, "orders/confirmation.html", {"order": order})

# Create your views here.
