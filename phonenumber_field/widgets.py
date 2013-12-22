#-*- coding: utf-8 -*-
from django.forms import TextInput
from django.forms.widgets import MultiWidget
from phonenumber_field.phonenumber import PhoneNumber, to_python

class PhoneNumberWidget(MultiWidget):
    """
    A Widget that splits phone number input into:
    - an input for the country code prefix
    - an input for local phone number
    - an input for extension
    """
    def __init__(self, attrs=None, initial=None):
        widgets = (TextInput(),TextInput(),TextInput())
        super(PhoneNumberWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if not isinstance(value, PhoneNumber):
            value = to_python(value)
        return [value.country_code, value.national_number, value.extension]

    def value_from_datadict(self, data, files, name):
        country_code, national_number, extension = super(PhoneNumberWidget, self).value_from_datadict(data, files, name)
        if country_code:
            country_code = "+%s" % country_code
        if extension:
            extension = "x%s" % extension
        return '%s%s%s' % (country_code, national_number, extension)