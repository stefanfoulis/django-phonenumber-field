# -*- coding: utf-8 -*-

import sys
import phonenumbers
from django.core import validators
from phonenumbers.phonenumberutil import NumberParseException
from django.conf import settings


# Snippet from the `six` library to help with Python3 compatibility
if sys.version_info[0] == 3:
    string_types = str
else:
    string_types = basestring


class PhoneNumber(phonenumbers.phonenumber.PhoneNumber):
    """
    A extended version of phonenumbers.phonenumber.PhoneNumber that provides
    some neat and more pythonic, easy to access methods. This makes using a
    PhoneNumber instance much easier, especially in templates and such.
    """
    format_map = {
        'E164': phonenumbers.PhoneNumberFormat.E164,
        'INTERNATIONAL': phonenumbers.PhoneNumberFormat.INTERNATIONAL,
        'NATIONAL': phonenumbers.PhoneNumberFormat.NATIONAL,
        'RFC3966': phonenumbers.PhoneNumberFormat.RFC3966,
    }

    @classmethod
    def from_string(cls, phone_number, region=None):
        phone_number_obj = cls()
        if region is None:
            region = (getattr(settings, 'PHONENUMBER_DEFAULT_REGION', None)
                      or getattr(settings, 'PHONENUMER_DEFAULT_REGION', None))
        phonenumbers.parse(number=phone_number, region=region,
                           keep_raw_input=True, numobj=phone_number_obj)
        return phone_number_obj

    def __unicode__(self):
        format_string = getattr(settings, 'PHONENUMBER_DEFAULT_FORMAT', 'E164')
        fmt = self.format_map[format_string]
        if self.is_valid():
            return self.format_as(fmt)
        return self.raw_input

    def is_valid(self):
        """
        checks whether the number supplied is actually valid
        """
        return phonenumbers.is_valid_number(self)

    def format_as(self, format):
        if self.is_valid():
            return phonenumbers.format_number(self, format)
        else:
            return self.raw_input

    @property
    def as_international(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    @property
    def as_e164(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.E164)

    @property
    def as_national(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.NATIONAL)

    @property
    def as_rfc3966(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.RFC3966)

    def __len__(self):
        return len(self.__unicode__())

    def __eq__(self, other):
        if type(other) == PhoneNumber:
            return self.as_e164 == other.as_e164
        else:
            return super(PhoneNumber, self).__eq__(other)


def to_python(value):
    if value in validators.EMPTY_VALUES:  # None or ''
        phone_number = None
    elif value and isinstance(value, string_types):
        try:
            phone_number = PhoneNumber.from_string(phone_number=value)
        except NumberParseException:
            # the string provided is not a valid PhoneNumber.
            phone_number = PhoneNumber(raw_input=value)
    elif (isinstance(value, phonenumbers.phonenumber.PhoneNumber) and
          not isinstance(value, PhoneNumber)):
        phone_number = PhoneNumber(value)
    elif isinstance(value, PhoneNumber):
        phone_number = value
    else:
        # TODO: this should somehow show that it has invalid data, but not
        #       completely die for bad data in the database.
        #       (Same for the NumberParseException above)
        phone_number = None
    return phone_number
