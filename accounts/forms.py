from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length=150, label="Full name")

    class Meta:
        model = User
        fields = ("name", "email", "phone_number", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            classes = "mt-2 w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-emerald-500"
            if field_name in {"password1", "password2"}:
                field.widget = forms.PasswordInput(attrs={"class": classes})
            else:
                field.widget.attrs.update({"class": classes})

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"].strip()
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone_number

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        name = self.cleaned_data["name"].strip()
        email = self.cleaned_data["email"].strip().lower()
        user.username = email
        user.first_name = name
        user.email = email
        user.phone_number = self.cleaned_data["phone_number"].strip()
        if commit:
            user.save()
        return user


class StyledAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Email", widget=forms.EmailInput(attrs={"autocomplete": "email"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        widget_class = "mt-2 w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-emerald-500"
        self.fields["username"].widget.attrs.update({"class": widget_class})
        self.fields["password"].widget.attrs.update({"class": widget_class})