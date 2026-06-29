from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterForm


class RegisterView(CreateView):
	form_class = RegisterForm
	template_name = "accounts/register.html"
	success_url = reverse_lazy("core:home")

	def form_valid(self, form):
		response = super().form_valid(form)
		login(self.request, self.object)
		messages.success(self.request, "Registration successful. Welcome to Tefas Pharmacy.")
		return response


def profile_view(request):
	return render(request, "accounts/profile.html", {})

# Create your views here.
