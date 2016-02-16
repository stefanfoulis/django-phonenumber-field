from django import forms
from testapp.models import TestModelBlankPhone
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget


class TestFormWidget(forms.ModelForm):
    phone = PhoneNumberField(required=False, widget=PhoneNumberPrefixWidget())

    class Meta:
        model = TestModelBlankPhone
        fields = "__all__"
