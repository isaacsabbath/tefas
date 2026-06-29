from django import forms

from .models import PickupLocation


class CheckoutForm(forms.Form):
    delivery_method = forms.ChoiceField(
        choices=(
            ("home", "Home Delivery"),
            ("pickup", "Pickup"),
        ),
        widget=forms.RadioSelect,
    )
    delivery_address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    pickup_location = forms.ModelChoiceField(
        queryset=PickupLocation.objects.filter(is_active=True),
        required=False,
        empty_label="Select a pickup location",
    )
    phone_number = forms.CharField(max_length=12)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_class = "mt-2 w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-emerald-500"
        self.fields["delivery_address"].widget.attrs.update({"class": f"{base_class} min-h-28"})
        self.fields["pickup_location"].widget.attrs.update({"class": base_class})
        self.fields["phone_number"].widget.attrs.update({"class": base_class})
        self.fields["delivery_method"].widget.attrs.update({"class": "space-y-3"})

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"].strip()
        if not phone_number.startswith("2547") or len(phone_number) != 12:
            raise forms.ValidationError("Enter a valid Kenyan phone number in the format 2547XXXXXXXX.")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        delivery_method = cleaned_data.get("delivery_method")
        delivery_address = cleaned_data.get("delivery_address")
        pickup_location = cleaned_data.get("pickup_location")

        if delivery_method == "home" and not delivery_address:
            self.add_error("delivery_address", "Enter a delivery address for home delivery.")
        if delivery_method == "pickup" and not pickup_location:
            self.add_error("pickup_location", "Choose a pickup location.")
        return cleaned_data