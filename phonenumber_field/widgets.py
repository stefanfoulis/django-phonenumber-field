# -*- coding: utf-8 -*-

from babel import Locale

from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE

from django.utils import translation
from django.forms import Select, TextInput
from django.forms.widgets import MultiWidget

from phonenumber_field.phonenumber import PhoneNumber


class PhonePrefixSelect(Select):

    initial = None

    def __init__(self, initial=None):
        choices = [('', '---------')]
        region_choices = []

        lang_code = translation.get_language()
        if not lang_code:
            # if translations are temporarily deactivated or NA
            lang_code = "en-us"

        locale = Locale.parse(lang_code, sep='-')
        for prefix, values in _COUNTRY_CODE_TO_REGION_CODE.iteritems():
            prefix = '+%d' % prefix
            
            if initial and initial in values:
                self.initial = prefix
                
            for i, country_code in enumerate(values):
                country_name = locale.territories.get(country_code)
                if country_name:
                    opt = (prefix, u'%s %s' % (country_name, prefix))
                    if i == 0:
                        choices.append(opt)
                    else:
                        region_choices.append(opt)

        choices = sorted(choices, key=lambda item: item[1])
        choices += sorted(region_choices, key=lambda item: item[1])

        return super(PhonePrefixSelect, self).__init__(choices=choices)

    def render(self, name, value, *args, **kwargs):
        return super(PhonePrefixSelect, self).render(
            name, value or self.initial, *args, **kwargs)


class PhoneNumberPrefixWidget(MultiWidget):
    """
    A Widget that splits phone number input into:
    - a country select box for phone prefix
    - an input for local phone number
    """
    def __init__(self, attrs=None, initial=None):
        widgets = (PhonePrefixSelect(initial), TextInput(),)
        super(PhoneNumberPrefixWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if type(value) == PhoneNumber:
                if value.country_code and value.national_number:
                    return ["+%d" % value.country_code, value.national_number]
            else:
                return value.split('.')
        return [None, None]

    def value_from_datadict(self, data, files, name):
        values = super(PhoneNumberPrefixWidget, self).value_from_datadict(
            data, files, name)
        return '%s.%s' % tuple(values)
