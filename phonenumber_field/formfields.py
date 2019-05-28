# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import phonenumbers
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.fields import CharField
from django.utils.translation import ugettext as _

from phonenumber_field.phonenumber import to_python, validate_region
from phonenumber_field.validators import validate_international_phonenumber


class PhoneNumberField(CharField):
    default_error_messages = {}
    default_validators = [validate_international_phonenumber]

    def __init__(self, *args, **kwargs):
        self.region = kwargs.pop("region", None)
        validate_region(self.region)

        if self.region:
            number = phonenumbers.example_number(self.region)
            example_number = to_python(number).as_national
            # Translators: {example_number} is a national phone number.
            error_message = _(
                "Enter a valid phone number (e.g. {example_number}) "
                "or a number with an international call prefix."
            )
        else:
            example_number = "+12125552368"  # Ghostbusters
            # Translators: {example_number} is an international phone number.
            error_message = _("Enter a valid phone number (e.g. {example_number}).")
        self.default_error_messages["invalid"] = error_message.format(
            example_number=example_number
        )

        super(PhoneNumberField, self).__init__(*args, **kwargs)
        self.widget.input_type = "tel"

    def to_python(self, value):
        phone_number = to_python(value, region=self.region)

        if phone_number in validators.EMPTY_VALUES:
            return self.empty_value

        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages["invalid"])

        return phone_number
