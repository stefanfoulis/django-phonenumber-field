# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.forms.fields import CharField
from django.core.exceptions import ValidationError
from phonenumber_field.validators import validate_international_phonenumber
from phonenumber_field.phonenumber import to_python


class PhoneNumberField(CharField):
    default_error_messages = {
        'invalid': _('Enter a valid phone number.'),
    }
    default_validators = [validate_international_phonenumber]

    def to_python(self, value):
        phone_number = to_python(value)
        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages['invalid'])
        return phone_number
