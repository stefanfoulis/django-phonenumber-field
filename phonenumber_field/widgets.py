from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.forms import Select, TextInput
from django.forms.widgets import MultiWidget
from django.utils import translation
from phonenumbers import PhoneNumberFormat
from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE
from phonenumbers.phonenumberutil import (
    national_significant_number,
    region_code_for_number,
)

from phonenumber_field.phonenumber import PhoneNumber

try:
    import babel
except ModuleNotFoundError:
    babel = None


class PhonePrefixSelect(Select):
    initial = None

    def __init__(self, initial=None):
        if babel is None:
            raise ImproperlyConfigured(
                "The PhonePrefixSelect widget requires the babel package be installed."
            )

        choices = [("", "---------")]
        language = translation.get_language() or settings.LANGUAGE_CODE
        locale = babel.Locale(translation.to_locale(language))
        if not initial:
            initial = getattr(settings, "PHONENUMBER_DEFAULT_REGION", None)
        for prefix, values in _COUNTRY_CODE_TO_REGION_CODE.items():
            prefix = "+%d" % prefix
            if initial and initial in values:
                self.initial = prefix
            for country_code in values:
                country_name = locale.territories.get(country_code)
                if country_name:
                    choices.append((prefix, "{} {}".format(country_name, prefix)))
        super().__init__(choices=sorted(choices, key=lambda item: item[1]))

    def get_context(self, name, value, attrs):
        return super().get_context(name, value or self.initial, attrs)


class PhoneNumberPrefixWidget(MultiWidget):
    """
    A Widget that splits phone number input into:
    - a country select box for phone prefix
    - an input for local phone number
    """

    def __init__(self, attrs=None, initial=None):
        widgets = (PhonePrefixSelect(initial), TextInput())
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if type(value) == PhoneNumber:
                if value.country_code and value.national_number:
                    return [
                        "+%d" % value.country_code,
                        national_significant_number(value),
                    ]
            else:
                return value.split(".")
        return [None, ""]

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        if all(values):
            return "%s.%s" % tuple(values)
        return ""


class PhoneNumberInternationalFallbackWidget(TextInput):
    """
    A Widget that allows a phone number in a national format, but if given
    an international number will fall back to international format
    """

    def __init__(self, region=None, attrs=None):
        if region is None:
            region = getattr(settings, "PHONENUMBER_DEFAULT_REGION", None)
        self.region = region
        super().__init__(attrs)

    def format_value(self, value):
        if isinstance(value, PhoneNumber):
            number_region = region_code_for_number(value)
            if self.region != number_region:
                formatter = PhoneNumberFormat.INTERNATIONAL
            else:
                formatter = PhoneNumberFormat.NATIONAL
            return value.format_as(formatter)
        return super().format_value(value)
