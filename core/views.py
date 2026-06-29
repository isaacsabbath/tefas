from django.db.models import Q
from django.shortcuts import render

from catalog.models import Product


def home(request):
	query = request.GET.get("q", "").strip()
	products = Product.objects.filter(is_active=True).select_related("category")
	if query:
		products = products.filter(Q(name__icontains=query) | Q(short_description__icontains=query) | Q(description__icontains=query))
	return render(request, "core/home.html", {"products": products, "query": query})

# Create your views here.
