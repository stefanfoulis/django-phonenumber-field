from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from phonenumber_field.phonenumber import PhoneNumber, to_python, validate_region


class PhoneNumberField(serializers.CharField):
    default_error_messages = {"invalid": _("Enter a valid phone number.")}

    def __init__(
        self,
        *args,
        region=None,
        get_str_value=False,
        split_representation=False,
        **kwargs,
    ):
        """
        :keyword str region: 2-letter country code as defined in ISO 3166-1.
            When not supplied, defaults to :setting:`PHONENUMBER_DEFAULT_REGION`

        :keyword bool get_str_value: boolean value to get string type of
            phone number in validated data when needed

        : keyword bool split_representation: boolean value to represent country code
            and number separately
        """
        super().__init__(*args, **kwargs)
        validate_region(region)
        self.region = region or getattr(settings, "PHONENUMBER_DEFAULT_REGION", None)
        self.get_str_value = get_str_value
        self.split_representation = split_representation

    def to_internal_value(self, data):
        if isinstance(data, PhoneNumber):
            phone_number = data
        else:
            str_value = super().to_internal_value(data)
            phone_number = to_python(str_value, region=self.region)

        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages["invalid"])

        return self.get_str_value and str(phone_number) or phone_number

    def to_representation(self, value):
        return (
            self.split_representation
            and {
                "country_code": f"+{value.country_code}",
                "number": value.national_number,
            }
            or super().to_representation(value=value)
        )
