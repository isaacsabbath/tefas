import json

from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .mpesa import process_callback_payload


@csrf_exempt
def callback_view(request):
	if request.method != "POST":
		return HttpResponseBadRequest("POST required")
	try:
		payload = json.loads(request.body.decode("utf-8")) if request.body else {}
	except json.JSONDecodeError:
		return JsonResponse({"detail": "Invalid JSON payload."}, status=400)
	process_callback_payload(payload)
	return JsonResponse({"detail": "Callback received."})

# Create your views here.
