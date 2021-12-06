from django import forms

from phonenumber_field.formfields import PhoneNumberField

from .models import NullablePhoneNumber, TestModelRegionAR


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = NullablePhoneNumber
        fields = ["phone_number"]


class CustomPhoneNumberFormField(PhoneNumberField):
    pass


class ARPhoneNumberForm(forms.ModelForm):
    class Meta:
        model = TestModelRegionAR
        fields = ["phone"]
