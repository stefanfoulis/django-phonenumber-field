#-*- coding: utf-8 -*-
from django.forms import Select, TextInput
from django.forms.widgets import MultiWidget
from django.template import Context
from django.template.loader import get_template
from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE
from phonenumber_field.phonenumber import PhoneNumber, to_python

class CountryCodeSelect(Select):
    initial = None

    def __init__(self, phone_widget, initial=None):
        self.phone_widget = phone_widget
        choices = [('', '---------')]
        for prefix, values in _COUNTRY_CODE_TO_REGION_CODE.iteritems():
            if initial and initial in values:
                self.initial = prefix
            for code in values:
                choices.append((u'%s' % prefix, u'%s (%s)' % (code, prefix)))
        return super(CountryCodeSelect, self).__init__(choices=sorted(choices, key=lambda item: item[1]))

    def render(self, name, value, *args, **kwargs):
        if value == self.phone_widget.empty_country_code:
            value = ""
        else:
            value = value or self.initial
        return super(CountryCodeSelect, self).render(name, value, *args, **kwargs)

class PhoneNumberWidget(MultiWidget):
    """
    A Widget that splits phone number input into:
    - an input for the country code prefix
    - an input for local phone number
    - an input for extension
    """
    template_name = "phonenumber_field/format_phone_number_widget_output.html"
    
    def __init__(self, attrs=None, initial=None):
        widgets = (CountryCodeSelect(self),TextInput(),TextInput())
        
        def f(i):
            def id_for_label(id_):
                if id_.endswith("_0"):
                    id_ = id_[:-2]
                return "{0}_{1}".format(id_, i) if id_ else id_
            return id_for_label
        
        for i, widget in enumerate(widgets):
            widget.id_for_label = f(i)
        
        super(PhoneNumberWidget, self).__init__(widgets, attrs)
        self._empty_country_code = [None]
        self._base_id = ""
        self.country_code = None
        self.national_number = None
        self.extension = None
    
    @property
    def empty_country_code(self):
        return self._empty_country_code[0]
    
    @empty_country_code.setter
    def empty_country_code(self, value):
        self._empty_country_code[0] = value

    def decompress(self, value):
        if not isinstance(value, PhoneNumber):
            value = to_python(value)
        if isinstance(value, PhoneNumber):
            return [value.country_code, value.national_number, value.extension]
        else:
            return [self.country_code, self.national_number, self.extension]

    def value_from_datadict(self, data, files, name):
        country_code, national_number, extension = super(PhoneNumberWidget, self).value_from_datadict(data, files, name)
        if country_code or (self.empty_country_code and national_number):
            if country_code:
                self.country_code = country_code
            country_code = "+{0}-".format(country_code or self.empty_country_code)
        if national_number:
            self.national_number = national_number
        if extension:
            self.extension = extension
            extension = "x%s" % extension
        return '%s%s%s' % (country_code, national_number, extension)
    
    def render(self, *args, **kwargs):
        attrs = kwargs.get("attrs", None) or {}
        self._base_id = attrs.get("id", "")
        return super(PhoneNumberWidget, self).render(*args, **kwargs)
    
    def format_output(self, rendered_widgets):
        c = Context({
            "code": rendered_widgets[0],
            "code_id": "{0}_0".format(self._base_id),
            "number": rendered_widgets[1],
            "number_id": "{0}_1".format(self._base_id),
            "extension": rendered_widgets[2],
            "extension_id": "{0}_2".format(self._base_id),
        })
        t = get_template(self.template_name)
        return t.render(c)
    
    @property
    def country_code_widget(self):
        return self.widgets[0]
    
    @property
    def national_number_widget(self):
        return self.widgets[1]
    
    @property
    def extension_widget(self):
        return self.widgets[2]