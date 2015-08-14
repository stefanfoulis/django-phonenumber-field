#-*- coding: utf-8 -*-
import logging
from django.core.management import call_command
from django.db.models import Q
from django.forms import Select, TextInput
from django.forms.widgets import MultiWidget
from django.template import Context
from django.template.loader import get_template
from django.utils.encoding import force_text
from django.utils.six import StringIO, string_types
from json import dumps, loads
from .models import CountryCode
from .phonenumber import PhoneNumber

logger = logging.getLogger(".".join(("django", __name__)))

class CountryCodeSelectChoicesIterator(object):
    def __init__(self, widget):
        self.widget = widget
    
    def __iter__(self):
        return iter(self.widget.get_choices())

class CountryCodeSelect(Select):
    def __init__(self, **kwargs):
        kwargs.pop("choices", None)
        super(CountryCodeSelect, self).__init__(**kwargs)
        self.choices = CountryCodeSelectChoicesIterator(self)

    def render(self, name, value, *args, **kwargs):
        if isinstance(value, CountryCode):
            value = self.country_code_to_choice(value)
        return super(CountryCodeSelect, self).render(name, value, *args, **kwargs)
    
    def value_from_datadict(self, *args, **kwargs):
        """
        Returns a country code model instance
        """
        code = None
        choice = super(CountryCodeSelect, self).value_from_datadict(*args, **kwargs)
        if choice:
            try:
                code = self.country_code_from_choice(choice)
            except (CountryCode.DoesNotExist, ValueError):
                pass
        return code
    
    def get_choices(self):
        choices = self.get_country_code_choices()
        choices = self.sort_choices(choices)
        choices = self.insert_empty_choice(choices)
        return choices
    
    def country_code_to_choice(self, country_code):
        return dumps(country_code.natural_key(), separators=(',',':'))

    def country_code_to_display(self, country_code):
        return force_text(country_code)
    
    def country_code_from_choice(self, choice):
        return CountryCode.objects.get_by_natural_key(*loads(choice))
    
    def get_value_from_phonenumber(self, phonenumber):
        value = None
        if isinstance(phonenumber, PhoneNumber):
            region_code = phonenumber.region_code
            calling_code = phonenumber.country_code
            try:
                value = CountryCode.objects.get_by_natural_key(region_code, calling_code)
            except CountryCode.DoesNotExist:
                pass
        return value
    
    def get_country_code_choices(self):
        choices = []
        country_codes = self.get_country_codes()
        for country_code in country_codes:
            choices.append((self.country_code_to_choice(country_code), self.country_code_to_display(country_code)))
        return choices
    
    def get_country_codes(self):
        country_codes = self.queryset.all()
        if not country_codes and not CountryCode.objects.exists():
            logger.critical("No CountryCode instances detected in the database.  Running the 'autopopulate_phonenumber_field_models' management command.")
            stdout = StringIO()
            stderr = StringIO()
            try:
                call_command("autopopulate_phonenumber_field_models", stdout=stdout, stderr=stderr)
            finally:
                logger.critical(stdout.getvalue())
                logger.critical(stderr.getvalue())
                stdout.close()
                stderr.close()
            country_codes = self.queryset.all()
        return country_codes
    
    def sort_choices(self, choices):
        if not isinstance(choices, list):
            choices = list(choices)
        choices.sort(key=lambda c: c[1])
        return choices
    
    def insert_empty_choice(self, choices):
        if not isinstance(choices, list):
            choices = list(choices)
        choices.insert(0, self.empty_choice)
        return choices
    
    @property
    def empty_choice(self):
        return ('', '---------')
    
    @property
    def queryset(self):
        return CountryCode.objects.filter(
            Q(region_code_obj__isnull=True) | Q(region_code_obj__active=True),
            active=True,
            calling_code_obj__active=True,
        )

class PhoneNumberWidget(MultiWidget):
    """
    A Widget that splits phone number input into:
    - an input for the country code prefix
    - an input for local phone number
    - an input for extension
    """
    template_name = "phonenumber_field/format_phone_number_widget_output.html"
    country_code = None
    national_number = ""
    extension = ""
    widgets = (CountryCodeSelect, TextInput, TextInput)
    _base_id = ""
    
    def __init__(self, attrs=None):
        widgets = [w() if isinstance(w, type) else w for w in self.widgets]
        
        def f(i):
            def id_for_label(id_):
                if id_.endswith("_0"):
                    id_ = id_[:-2]
                return "{0}_{1}".format(id_, i) if id_ else id_
            return id_for_label

        for i, widget in enumerate(widgets):
            widget.id_for_label = f(i)

        super(PhoneNumberWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        data = [self.country_code, self.national_number, self.extension]
        if not any(data):
            if isinstance(value, string_types):
                try:
                    value = PhoneNumber.from_string(value)
                except:
                    pass
            if isinstance(value, PhoneNumber):
                country_code = self.country_code_widget.get_value_from_phonenumber(value)
                data = [country_code, value.national_number, value.extension]
        return data
    
    def value_from_datadict(self, data, files, name):
        country_code, national_number, extension = super(PhoneNumberWidget, self).value_from_datadict(data, files, name)
        region_code_prefix = ""
        if country_code:
            self.country_code = country_code
            if country_code.region_code:
                region_code_prefix = "{}{}".format(country_code.region_code, PhoneNumber.region_code_sep)
            country_code = force_text("+{0}-").format(country_code.calling_code)
        if national_number:
            self.national_number = national_number
        if extension:
            self.extension = extension
            extension = "x%s" % extension
        return force_text('%s%s%s%s') % (region_code_prefix, country_code, national_number, extension or "")
    
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
