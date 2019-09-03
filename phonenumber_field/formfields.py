import phonenumbers
from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.fields import CharField
from django.utils.translation import gettext as _

from phonenumber_field.phonenumber import to_python, validate_region
from phonenumber_field.validators import validate_international_phonenumber


class PhoneNumberField(CharField):
    default_validators = [validate_international_phonenumber]

    def __init__(self, *args, region=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget.input_type = "tel"

        validate_region(region)
        self.region = region

        if "invalid" not in self.error_messages:
            # Translators: {example_number} is a national phone number.
            error_message = _(
                "Enter a valid phone number (e.g. {example_number}) "
                "or a number with an international call prefix."
            )
            if self.region:
                number = phonenumbers.example_number(region)
            else:
                number = phonenumbers.example_number(
                    getattr(settings, "PHONENUMBER_DEFAULT_REGION", None)
                )
            example_number = to_python(number).as_national
            self.error_messages["invalid"] = error_message.format(
                example_number=example_number
            )

    def to_python(self, value):
        phone_number = to_python(value, region=self.region)

        if phone_number in validators.EMPTY_VALUES:
            return self.empty_value

        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages["invalid"])

        return phone_number
