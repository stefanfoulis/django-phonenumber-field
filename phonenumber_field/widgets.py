#-*- coding: utf-8 -*-
from django.forms import Select, TextInput
from django.forms.widgets import MultiWidget
from django.template import Context
from django.template.loader import get_template
from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE
from phonenumber_field.phonenumber import PhoneNumber, to_python

class CountryCodeSelect(Select):
    initial = None

    def __init__(self, initial=None):
        choices = [('', '---------')]
        for prefix, values in _COUNTRY_CODE_TO_REGION_CODE.iteritems():
            if initial and initial in values:
                self.initial = prefix
            for code in values:
                choices.append((u'%s' % prefix, u'%s (%s)' % (code, prefix)))
        return super(CountryCodeSelect, self).__init__(choices=sorted(choices, key=lambda item: item[1]))

    def render(self, name, value, *args, **kwargs):
        return super(CountryCodeSelect, self).render(name, value or self.initial, *args, **kwargs)

class PhoneNumberWidget(MultiWidget):
    """
    A Widget that splits phone number input into:
    - an input for the country code prefix
    - an input for local phone number
    - an input for extension
    """
    def __init__(self, attrs=None, initial=None):
        widgets = (CountryCodeSelect(),TextInput(),TextInput())
        super(PhoneNumberWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if not isinstance(value, PhoneNumber):
            value = to_python(value)
        if isinstance(value, PhoneNumber):
            return [value.country_code, value.national_number, value.extension]
        else:
            return [None, None, None]

    def value_from_datadict(self, data, files, name):
        country_code, national_number, extension = super(PhoneNumberWidget, self).value_from_datadict(data, files, name)
        if country_code:
            country_code = "+%s" % country_code
        if extension:
            extension = "x%s" % extension
        return '%s%s%s' % (country_code, national_number, extension)
    
    def format_output(self, rendered_widgets):
        c = Context({
            "code": rendered_widgets[0],
            "number": rendered_widgets[1],
            "extension": rendered_widgets[2],            
        })
        t = get_template("phonenumber_field/format_phone_number_widget_output.html")
        return t.render(c)