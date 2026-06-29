import base64
import logging
from decimal import Decimal

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from orders.models import Order

logger = logging.getLogger(__name__)


class MpesaError(Exception):
    pass


class MpesaNetworkError(MpesaError):
    pass


class MpesaApiError(MpesaError):
    pass


def _timestamp() -> str:
    return timezone.now().strftime("%Y%m%d%H%M%S")


def _password(timestamp: str) -> str:
    raw = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
    return base64.b64encode(raw).decode()


def _normalized_phone(phone_number: str) -> str:
    phone_number = phone_number.strip()
    if phone_number.startswith("+"):
        phone_number = phone_number[1:]
    return phone_number


def get_access_token() -> str:
    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    try:
        response = requests.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET), timeout=30)
    except requests.RequestException as exc:
        logger.exception("Failed to reach M-Pesa token endpoint")
        raise MpesaNetworkError("Unable to reach M-Pesa token endpoint.") from exc

    if response.status_code != 200:
        logger.error("M-Pesa token error: %s", response.text)
        raise MpesaApiError("M-Pesa rejected the token request.")

    token = response.json().get("access_token")
    if not token:
        raise MpesaApiError("M-Pesa token response did not include an access token.")
    return token


def build_stk_payload(order: Order) -> dict:
    timestamp = _timestamp()
    amount = int(order.total_amount)
    return {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": _password(timestamp),
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": _normalized_phone(order.phone_number),
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": _normalized_phone(order.phone_number),
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": str(order.order_number),
        "TransactionDesc": f"Tefas Pharmacy order {order.order_number}",
    }


def initiate_stk_push(order: Order) -> dict:
    url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    token = get_access_token()
    payload = build_stk_payload(order)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
    except requests.RequestException as exc:
        logger.exception("Failed to reach M-Pesa STK endpoint")
        raise MpesaNetworkError("Unable to reach M-Pesa STK push endpoint.") from exc

    try:
        data = response.json()
    except ValueError as exc:
        logger.error("M-Pesa returned invalid JSON: %s", response.text)
        raise MpesaApiError("M-Pesa returned an invalid response.") from exc

    if response.status_code != 200 or data.get("ResponseCode") not in {"0", 0, None}:
        logger.error("M-Pesa STK error: %s", data)
        raise MpesaApiError(data.get("errorMessage") or data.get("ResponseDescription") or "M-Pesa STK push failed.")

    return data


@transaction.atomic
def process_callback_payload(payload: dict) -> None:
    callback = payload.get("Body", {}).get("stkCallback", {})
    checkout_request_id = callback.get("CheckoutRequestID")
    result_code = callback.get("ResultCode")
    result_desc = callback.get("ResultDesc")
    metadata_items = callback.get("CallbackMetadata", {}).get("Item", [])
    metadata = {item.get("Name"): item.get("Value") for item in metadata_items if item.get("Name")}

    try:
        order = Order.objects.select_for_update().get(mpesa_checkout_request_id=checkout_request_id)
    except Order.DoesNotExist:
        logger.error("Callback received for unknown CheckoutRequestID=%s", checkout_request_id)
        return

    if result_code == 0:
        order.payment_status = Order.PaymentStatus.PAID
        order.status = Order.Status.PAID
        order.mpesa_receipt_number = metadata.get("MpesaReceiptNumber")
    else:
        order.payment_status = Order.PaymentStatus.FAILED
        order.status = Order.Status.PENDING
        logger.warning("M-Pesa payment failed for order %s: %s", order.order_number, result_desc)

    order.save(update_fields=["payment_status", "status", "mpesa_receipt_number", "updated_at"])