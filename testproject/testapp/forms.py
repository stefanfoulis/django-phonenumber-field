from django import forms
from .models import NullablePhoneNumber


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = NullablePhoneNumber
        fields = ["phone_number"]
