# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms.fields import CharField
from django.utils.translation import ugettext_lazy as _

from phonenumbers import PhoneNumberFormat
from phonenumber_field.phonenumber import PhoneNumber, to_python
from phonenumber_field.validators import validate_international_phonenumber
from phonenumbers.phonenumberutil import region_code_for_number


class PhoneNumberField(CharField):
    default_error_messages = {
        'invalid': _('Enter a valid phone number.'),
    }
    default_validators = [validate_international_phonenumber]

    def __init__(self, *args, **kwargs):
        super(PhoneNumberField, self).__init__(*args, **kwargs)
        self.widget.input_type = 'tel'

    def to_python(self, value):
        if value in self.empty_values:
            return self.empty_value
        phone_number = to_python(value)
        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages['invalid'])
        return phone_number


class PhoneNumberRegionFallbackField(PhoneNumberField):
    def __init__(self, *args, **kwargs):
        self.default_region = kwargs.pop('region', settings.PHONENUMBER_DEFAULT_REGION)
        super(PhoneNumberRegionFallbackField, self).__init__(*args, **kwargs)

    def prepare_value(self, value):
        """Show numbers in the 'default_region' without region code."""
        if isinstance(value, PhoneNumber):
            if self.default_region == region_code_for_number(value):
                return value.as_national
            else:
                return value.as_international
        return value

    def to_python(self, value):
        """Consider numbers without region code numbers in 'default_region'."""
        if value in self.empty_values:
            return self.empty_value
        phone_number = to_python(value, self.default_region)
        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages['invalid'])
        return phone_number
