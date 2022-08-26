from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from phonenumber_field.phonenumber import to_python, validate_region


class PhoneNumberField(serializers.CharField):
    default_error_messages = {"invalid": _("Enter a valid phone number.")}

    def __init__(self, *args, region=None, **kwargs):
        super().__init__(*args, **kwargs)
        validate_region(region)
        self.region = region or getattr(settings, "PHONENUMBER_DEFAULT_REGION", None)

    def to_internal_value(self, data):
        str_value = super().to_internal_value(data)
        phone_number = to_python(str_value, region=self.region)
        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages["invalid"])
        return phone_number
