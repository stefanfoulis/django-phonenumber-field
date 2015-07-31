# -*- coding: utf-8 -*-

import sys
import phonenumbers
from django.conf import settings
from django.core import validators
from django.utils.encoding import force_text
from django.utils.six import string_types
from phonenumbers.phonenumberutil import NumberParseException


class PhoneNumber(phonenumbers.phonenumber.PhoneNumber):
    """
    A extended version of phonenumbers.phonenumber.PhoneNumber that provides
    some neat and more pythonic, easy to access methods. This makes using a
    PhoneNumber instance much easier, especially in templates and such.
    """
    _region_code = None
    region_code_sep = getattr(settings, 'PHONENUMBER_REGION_CODE_SEPARATOR', '|')
    format_map = {
        'E164': phonenumbers.PhoneNumberFormat.E164,
        'INTERNATIONAL': phonenumbers.PhoneNumberFormat.INTERNATIONAL,
        'NATIONAL': phonenumbers.PhoneNumberFormat.NATIONAL,
        'RFC3966': phonenumbers.PhoneNumberFormat.RFC3966,
    }
    
    def __init__(self, **kwargs):
        raw = kwargs.get("raw_input", None)
        if raw:
            region_code, phone_number = self.parse_region_code(raw)
            self.region_code = region_code
            kwargs["raw_input"] = phone_number
        
        super(PhoneNumber, self).__init__(**kwargs)
    
    @classmethod
    def from_string(cls, phone_number, region=None):
        if not isinstance(phone_number, string_types):
            raise TypeError("Supplied phone number was not a string")
        
        if not (isinstance(region, string_types) or region is None):
            raise TypeError("Supplied region was not a string or None")
        
        phone_number_obj = cls()
        
        region_code, phone_number = cls.parse_region_code(phone_number)
        
        if region is None:
            if region_code:
                region = region_code
            else:
                region = (getattr(settings, 'PHONENUMBER_DEFAULT_REGION', None)
                          or getattr(settings, 'PHONENUMER_DEFAULT_REGION', None))
        phonenumbers.parse(number=phone_number, region=region,
                           keep_raw_input=True, numobj=phone_number_obj)
        
        phone_number_obj.region_code = region
        
        return phone_number_obj
    
    @classmethod
    def parse_region_code(cls, value):
        if not isinstance(value, string_types):
            raise TypeError("Supplied value was not a string")
        
        result = value.split(cls.region_code_sep, 1)
        len_result = len(result)
        
        if len_result == 1:
            region_code, phone_number = (None, result[0])
        elif len_result == 2:
            region_code, phone_number = result
        else:
            region_code, phone_number = (None, "")
        
        return region_code, phone_number

    def __unicode__(self):
        format_string = getattr(settings, 'PHONENUMBER_DEFAULT_FORMAT', 'E164')
        fmt = self.format_map[format_string]
        return self.format_as(fmt)

    def is_valid(self):
        """
        checks whether the number supplied is actually valid
        """
        return phonenumbers.is_valid_number(self)

    def format_as(self, fmt, include_region_code=False):
        if self.is_valid():
            value = phonenumbers.format_number(self, fmt)
            if self.extension and fmt == phonenumbers.PhoneNumberFormat.E164:
                value = force_text("{}x{}").format(value, self.extension)
        else:
            value = self.raw_input
        if include_region_code and self.region_code:
            value = force_text("{}{}{}").format(self.region_code, self.region_code_sep, value)
        return value

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
    
    @property
    def region_code(self):
        return self._region_code
    
    @region_code.setter
    def region_code(self, value):
        if value is None:
            self._region_code = None
        elif isinstance(value, string_types):
            self._region_code = value.upper()
        else:
            raise TypeError("Supplied value must be None or a string.  Value was of type: %s" % type(value))

    def __len__(self):
        return len(self.__unicode__())


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
