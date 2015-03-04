# -*- coding: utf-8 -*-

from babel import Locale

from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE

from django.utils.translation import to_locale, get_language
from django.forms import Select, TextInput
from django.forms.widgets import MultiWidget

from phonenumber_field.phonenumber import PhoneNumber

import logging
logger = logging.getLogger('werkzeug')

class PhonePrefixSelect(Select):

    initial = None

    def __init__(self, initial=None, attrs=None):
	logger.critical(attrs)
        choices = [('', '---------')]
        locale = Locale(to_locale(get_language()))
        for prefix, values in _COUNTRY_CODE_TO_REGION_CODE.iteritems():
            prefix = '+%d' % prefix
            if initial and initial in values:
                self.initial = prefix
            for country_code in values:
                country_name = locale.territories.get(country_code)
                if country_name:
                    choices.append((prefix, u'%s %s' % (prefix, country_name)))
        return super(PhonePrefixSelect, self).__init__(
            choices=sorted(choices, key=lambda item: item[1]), attrs=attrs)

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
	phone_attrs = None
	prefix_attrs = None
	if attrs:		
	    prefix_class = attrs.get('prefix_class')
	    phone_class = attrs.get('phone_class')
	    del attrs['prefix_class']
	    del attrs['phone_class']

	    phone_attrs = attrs.copy()
	    phone_attrs['class'] = phone_class
	    prefix_attrs = attrs.copy()
	    prefix_attrs['class'] = prefix_class
	
        widgets = (PhonePrefixSelect(initial, attrs=prefix_attrs), TextInput(attrs=phone_attrs),)
        super(PhoneNumberPrefixWidget, self).__init__(widgets, attrs)

    # def format_output(self, rendered_widgets):
    #     """
    #     Given a list of rendered widgets (as strings), it inserts an HTML
    #     linebreak between them.
        
    #     Returns a Unicode string representing the HTML for the whole lot.
    #     """
    #     return "Prefix: %s Phone: %s" % (rendered_widgets[0], rendered_widgets[1])


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
