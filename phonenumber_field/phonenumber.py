#-*- coding: utf-8 -*-
import phonenumbers
from django.core import validators
from phonenumbers.phonenumberutil import NumberParseException
from django.conf import settings

class PhoneNumber(phonenumbers.phonenumber.PhoneNumber):
    """
    A extended version of phonenumbers.phonenumber.PhoneNumber that provides some neat and more pythonic, easy
    to access methods. This makes using a PhoneNumber instance much easier, especially in templates and such.
    """
    @classmethod
    def from_string(cls, phone_number):
        phone_number_obj = cls()
        region = getattr(settings,'PHONENUMER_DEFAULT_REGION', None)
        phonenumbers.parse(number=phone_number, region=region, keep_raw_input=True, numobj=phone_number_obj)
        return phone_number_obj

    def __str__(self):
        if self.is_valid():
            return self.as_e164
        return self.raw_input

    def __unicode__(self):
        return unicode(self.__str__())

    def original_unicode(self):
        return super(PhoneNumber, self).__unicode__()

    def is_valid(self):
        """
        checks wether the number supplied is actually valid
        """
        return bool(self.country_code and self.national_number)

    def format_as(self, format):
        if self.is_valid():
            return phonenumbers.format_number(self, format)
        else:
            return self.raw_input

    @property
    def as_international(self):
        return phonenumbers.format_number(self, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    @property
    def as_e164(self):
        return phonenumbers.format_number(self, phonenumbers.PhoneNumberFormat.E164)

    @property
    def as_national(self):
        return phonenumbers.format_number(self, phonenumbers.PhoneNumberFormat.NATIONAL)

    @property
    def as_rfc3966(self):
        return phonenumbers.format_number(self, phonenumbers.PhoneNumberFormat.RFC3966)

    def __len__(self):
        return len(self.__unicode__())


def to_python(value):
    if value in validators.EMPTY_VALUES:  # None or ''
        phone_number = None
    elif value and isinstance(value, basestring):
        try:
            phone_number = PhoneNumber.from_string(phone_number=value)
        except NumberParseException, e:
            # the string provided is not a valid PhoneNumber.
            phone_number = PhoneNumber(raw_input=value)
    elif isinstance(value, phonenumbers.phonenumber.PhoneNumber) and \
         not isinstance(value, PhoneNumber):
        phone_number = self.field.attr_class()
        phone_number.merge_from(value)
    elif isinstance(value, PhoneNumber):
        phone_number = value
    return phone_number