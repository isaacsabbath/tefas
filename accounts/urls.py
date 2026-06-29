from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import StyledAuthenticationForm
from .views import RegisterView, profile_view

app_name = "accounts"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html", authentication_form=StyledAuthenticationForm), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", profile_view, name="profile"),
]